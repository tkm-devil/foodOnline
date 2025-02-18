from django.shortcuts import reverse
from .models import User

def detectUser(user):
    print(f"User role: {user.role}")  # Add this debug line
    if user.role == User.CUSTOMER:
        redirectUrl = reverse("customerDashboard")
        print(f"Redirecting customer to: {redirectUrl}")  # Debug line
        return redirectUrl
    elif user.role == User.VENDOR:
        redirectUrl = reverse("vendorDashboard")
        print(f"Redirecting vendor to: {redirectUrl}")  # Debug line
        return redirectUrl
    elif user.is_superuser:
        return "/admin"
    else:
        print("No role matched, redirecting to home")  # Debug line
        return reverse("home")
