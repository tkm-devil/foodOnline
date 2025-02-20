from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def vendor_profile(request):
    return render(request, "vendor/vendor_profile.html")

@login_required
def menu_builder(request):
    return render(request, "vendor/menu_builder.html")

@login_required
def vendor_orders(request):
    return render(request, "vendor/vendor_orders.html")

@login_required
def vendor_earnings(request):
    return render(request, "vendor/vendor_earnings.html")

@login_required
def vendor_statements(request):
    return render(request, "vendor/vendor_statements.html")

@login_required
def change_password(request):
    return render(request, "vendor/change_password.html")