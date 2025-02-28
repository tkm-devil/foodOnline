from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum, F
from accounts.forms import UserProfileForm
from .forms import VendorRegistrationForm, VendorMenuItemForm
from .models import Order, OrderStatus, VendorMenuItem, Earnings, OrderItem, Vendor


@login_required
def vendor_profile(request):
    '''Allows vendors to update their profile information.'''
    user = request.user
    vendor = get_object_or_404(Vendor, user=user)
    profile = user.userprofile

    if request.method == "POST":
        vendor_form = VendorRegistrationForm(request.POST, request.FILES, instance=vendor)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if vendor_form.is_valid() and profile_form.is_valid():
            vendor_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("vendor_profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        vendor_form = VendorRegistrationForm(instance=vendor)
        profile_form = UserProfileForm(instance=profile)

    return render(request, "vendor/vendor_profile.html", {"vendor_form": vendor_form, "profile_form": profile_form, "vendor": vendor})


@login_required
def menu_builder(request):
    '''Allows vendors to view and manage their menu items.'''
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_items = VendorMenuItem.objects.filter(vendor=vendor)
    return render(request, "vendor/menu_builder.html", {"menu_items": menu_items, "vendor": vendor})


@login_required
def add_menu_item(request):
    """Allows vendors to add new menu items."""
    vendor = request.user.vendor

    if request.method == "POST":
        form = VendorMenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.vendor = vendor
            menu_item.save()
            messages.success(request, "Menu item added successfully!")
            return redirect("menu_builder")
    else:
        form = VendorMenuItemForm()

    return render(request, "vendor/menu_item_form.html", {"form": form})


@login_required
def edit_menu_item(request, item_id):
    '''Allows vendors to edit existing menu items.'''
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_item = get_object_or_404(VendorMenuItem, id=item_id, vendor=vendor)

    if request.method == "POST":
        form = VendorMenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item updated successfully!")
            return redirect("menu_builder")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = VendorMenuItemForm(instance=menu_item)

    return render(request, "vendor/menu_item_form.html", {"form": form, "vendor": vendor})


@login_required
def delete_menu_item(request, item_id):
    '''Allows vendors to delete menu items.'''
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_item = get_object_or_404(VendorMenuItem, id=item_id, vendor=vendor)
    menu_item.delete()
    messages.success(request, "Menu item deleted successfully!")
    return redirect("menu_builder")


@login_required
def vendor_orders(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    order_items = OrderItem.objects.filter(vendor=vendor).select_related("order", "menu_item")
    orders = {order_item.order for order_item in order_items}
    return render(request, "vendor/vendor_orders.html", {"orders": orders, "vendor": vendor})


@login_required
def order_details(request, order_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    order_items = OrderItem.objects.filter(order_id=order_id, vendor=vendor)

    if not order_items:
        messages.error(request, "You do not have any items in this order.")
        return redirect("vendor_orders")

    order = order_items.first().order
    return render(request, "vendor/order_details.html", {"order": order, "order_items": order_items, "vendor": vendor})


@login_required
def update_order_status(request, order_id, new_status):
    vendor = get_object_or_404(Vendor, user=request.user)
    order_items = OrderItem.objects.filter(order_id=order_id, vendor=vendor)

    if not order_items.exists():
        messages.error(request, "You do not have permission to update this order.")
        return redirect("vendor_orders")

    # Get the order from the first order item (since all order_items belong to the same order)
    order = order_items.first().order
    order.status = new_status
    order.save()  # Save only once instead of in a loop

    messages.success(request, f"Order #{order_id} marked as {new_status}.")
    return redirect("vendor_orders")


@login_required
def vendor_earnings(request):
    vendor = get_object_or_404(Vendor, user=request.user)

    # Calculate earnings only if there are completed orders
    earnings = OrderItem.objects.filter(vendor=vendor, order__status=OrderStatus.COMPLETED).aggregate(
        total_earnings=Sum(F("quantity") * F("price_at_order"))
    )

    total_earnings = earnings["total_earnings"] or 0  # Ensures no None values

    # Ensure the Earnings object exists and update it
    vendor_earnings, created = Earnings.objects.get_or_create(vendor=vendor)
    vendor_earnings.total_earnings = total_earnings
    vendor_earnings.pending_balance = total_earnings - vendor_earnings.last_payment
    vendor_earnings.save()

    # Fetch completed orders for the vendor
    completed_orders = vendor.order_items.filter(order__status=OrderStatus.COMPLETED).select_related("order")

    context = {
        "vendor": vendor,
        "total_earnings": vendor_earnings.total_earnings,
        "pending_balance": vendor_earnings.pending_balance,
        "last_payment": vendor_earnings.last_payment,
        "last_payment_date": vendor_earnings.last_payment_date,
        "completed_orders": completed_orders,  # Pass completed orders explicitly
    }

    return render(request, "vendor/vendor_earnings.html", context)


@login_required
def vendor_statements(request):
    vendor = get_object_or_404(Vendor, user=request.user)

    # Get completed orders that contain items from this vendor
    completed_orders = Order.objects.filter(
        order_items__vendor=vendor, status=OrderStatus.COMPLETED
    ).distinct().prefetch_related("order_items")

    # Define service fee percentage (modify if needed)
    SERVICE_FEE_PERCENTAGE = 5  # Assuming 10% platform cut

    orders_data = []
    for order in completed_orders:
        order_items = order.order_items.filter(vendor=vendor)
        total_earnings = sum(item.quantity * item.price_at_order for item in order_items)

        # Calculate service fee and net earnings
        service_fee = (SERVICE_FEE_PERCENTAGE / 100) * total_earnings
        net_earnings = total_earnings - service_fee

        orders_data.append({
            "id": order.id,
            "total_price": total_earnings,
            "service_fee": service_fee,
            "net_earnings": net_earnings,
            "date_completed": order.updated_at,
        })

    context = {"orders": orders_data, "vendor": vendor}
    return render(request, "vendor/vendor_statements.html", context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'vendor/change_password.html', {'form': form})