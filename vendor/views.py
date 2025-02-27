from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum
from accounts.forms import UserProfileForm
from .forms import VendorRegistrationForm, VendorMenuItemForm
from .models import Order, VendorMenuItem, Earnings, OrderItem, Vendor


@login_required
def vendor_profile(request):
    """Vendor can update their profile."""
    user = request.user
    vendor = get_object_or_404(Vendor, user=user)
    profile = vendor.user_profile  # Get associated UserProfile

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

    return render(
        request,
        "vendor/vendor_profile.html",
        {"vendor_form": vendor_form, "profile_form": profile_form, "vendor": vendor},
    )

@login_required
def menu_builder(request):
    """Vendor's menu management: lists menu items sold by this vendor."""
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_items = VendorMenuItem.objects.filter(vendor=vendor)  # Vendor-specific menu
    return render(request, "vendor/menu_builder.html", {"menu_items": menu_items, "vendor": vendor})


@login_required
def add_menu_item(request):
    """Vendor adds a new menu item (vendor-specific)."""
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.method == "POST":
        form = VendorMenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.vendor = vendor
            menu_item.save()
            messages.success(request, "Menu item added successfully!")
            return redirect("menu_builder")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = VendorMenuItemForm()

    return render(request, "vendor/menu_item_form.html", {"form": form, "vendor": vendor})


@login_required
def edit_menu_item(request, item_id):
    """Vendor edits an existing menu item (specific to them)."""
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
    """Vendor deletes their menu item."""
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_item = get_object_or_404(VendorMenuItem, id=item_id, vendor=vendor)
    menu_item.delete()
    messages.success(request, "Menu item deleted successfully!")
    return redirect("menu_builder")

@login_required
def vendor_orders(request):
    """Display all orders containing items sold by this vendor."""
    vendor = get_object_or_404(Vendor, user=request.user)

    # Fetch orders where this vendor has sold items
    order_items = OrderItem.objects.filter(vendor=vendor).select_related("order", "menu_item")
    orders = {order_item.order for order_item in order_items}  # Get unique orders

    return render(request, "vendor/vendor_orders.html", {"orders": orders, "vendor": vendor})


@login_required
def order_details(request, order_id):
    """View details of a single order, showing only the vendor's items."""
    vendor = get_object_or_404(Vendor, user=request.user)
    order_items = OrderItem.objects.filter(order_id=order_id, vendor=vendor)

    if not order_items:
        messages.error(request, "You do not have any items in this order.")
        return redirect("vendor_orders")

    order = order_items.first().order  # Get the related order

    return render(request, "vendor/order_details.html", {"order": order, "order_items": order_items, "vendor": vendor})


@login_required
def update_order_status(request, order_id, new_status):
    """Vendor can update the status of their portion of an order."""
    vendor = get_object_or_404(Vendor, user=request.user)

    # Get order items for this vendor only
    order_items = OrderItem.objects.filter(order_id=order_id, vendor=vendor)

    if not order_items:
        messages.error(request, "You do not have permission to update this order.")
        return redirect("vendor_orders")

    # Update the status of each item the vendor is responsible for
    for order_item in order_items:
        order_item.order.status = new_status
        order_item.order.save()

    messages.success(request, f"Order #{order_id} marked as {new_status}.")
    return redirect("vendor_orders")


@login_required
def vendor_earnings(request):
    """Vendor earnings summary, calculated from completed order items."""
    vendor = get_object_or_404(Vendor, user=request.user)

    earnings = OrderItem.objects.filter(vendor=vendor, order__status="Completed").aggregate(
        total_earnings=Sum('price_at_order', default=0)
    )

    vendor_earnings, created = Earnings.objects.get_or_create(vendor=vendor)
    vendor_earnings.total_earnings = earnings["total_earnings"]
    vendor_earnings.save()

    context = {
        "vendor": vendor,
        "total_earnings": vendor_earnings.total_earnings,
        "last_payment": vendor_earnings.last_payment,
        "last_payment_date": vendor_earnings.last_payment_date,
    }

    return render(request, "vendor/vendor_earnings.html", context)

@login_required
def vendor_statements(request):
    """Shows vendor's completed order history for financial tracking."""
    vendor = get_object_or_404(Vendor, user=request.user)

    order_items = OrderItem.objects.filter(vendor=vendor, order__status="Completed").select_related("order")
    orders = {order_item.order for order_item in order_items}

    context = {"orders": orders, "vendor": vendor}
    return render(request, "vendor/vendor_statements.html", context)

@login_required
def change_password(request):
    """Allow vendor to change their password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'vendor/change_password.html', {'form': form})
