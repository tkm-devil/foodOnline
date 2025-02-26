from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum, Max
from accounts.forms import UserProfileForm
from .forms import VendorRegistrationForm, MenuItemForm
from .models import Order, MenuItem, Earnings

@login_required
def vendor_profile(request):
    user = request.user
    vendor = user.vendor
    profile = vendor.user_profile  # Get the associated UserProfile

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
    vendor = request.user.vendor
    menu_items = MenuItem.objects.filter(vendor=vendor)  # Fetch vendor's menu items
    return render(request, "vendor/menu_builder.html", {"menu_items": menu_items, "vendor": vendor})

@login_required
def add_menu_item(request):
    vendor = request.user.vendor
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.vendor = vendor
            menu_item.save()
            messages.success(request, "Menu item added successfully!")
            return redirect("menu_builder")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MenuItemForm()
    
    return render(request, "vendor/menu_item_form.html", {"form": form, "vendor": vendor})

@login_required
def edit_menu_item(request, item_id):
    vendor = request.user.vendor
    menu_item = get_object_or_404(MenuItem, id=item_id, vendor=vendor)
    
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item updated successfully!")
            return redirect("menu_builder")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MenuItemForm(instance=menu_item)

    return render(request, "vendor/menu_item_form.html", {"form": form, "vendor": vendor})

@login_required
def delete_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id, vendor=request.user.vendor)
    menu_item.delete()
    messages.success(request, "Menu item deleted successfully!")
    return redirect("menu_builder")

@login_required
def vendor_orders(request):
    """Display all orders for the vendor, sorted by latest."""
    vendor = request.user.vendor
    orders = Order.objects.filter(vendor=vendor).select_related('customer').order_by('-created_at')
    return render(request, "vendor/vendor_orders.html", {"orders": orders, "vendor": vendor})

@login_required
def order_details(request, order_id):
    """View detailed order information."""
    vendor = request.user.vendor
    order = get_object_or_404(Order, id=order_id, vendor=vendor)
    return render(request, "vendor/order_details.html", {"order": order, "vendor": vendor})

@login_required
def update_order_status(request, order_id, new_status):
    """Update the order status (Processing → Completed / Cancelled)."""
    order = get_object_or_404(Order, id=order_id, vendor=request.user.vendor)
    
    if order.status == "Processing":
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} marked as {new_status}.")
    else:
        messages.error(request, "Order status update is not allowed.")

    return redirect("vendor_orders")

@login_required
def vendor_earnings(request):
    vendor = request.user.vendor
    earnings = Earnings.objects.filter(vendor=vendor).aggregate(
        total_earnings=Sum('total_earnings', default=0),
        last_payment=Max('last_payment', default=0),
        last_payment_date=Max('last_payment_date')
    )

    context = {
        "vendor": vendor,
        "total_earnings": earnings["total_earnings"],
        "last_payment": earnings["last_payment"],
        "last_payment_date": earnings["last_payment_date"],
    }
    
    return render(request, "vendor/vendor_earnings.html", context)

@login_required
def vendor_statements(request):
    vendor = request.user.vendor
    orders = Order.objects.filter(vendor=vendor).order_by('-created_at')  # Latest orders first

    context = {"orders": orders, "vendor": vendor}
    return render(request, "vendor/vendor_statements.html", context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'vendor/change_password.html', {'form': form})
