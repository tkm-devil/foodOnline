from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from vendor.forms import VendorRegistrationForm
from .forms import UserRegistrationForm, LoginForm
from .models import User, UserProfile

# Create your views here.

def registerUser(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login_view')  # Redirect to login instead of registerUser
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/registerUser.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)  # Auth via email
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("home")  # Redirect to home or dashboard
            else:
                messages.error(request, "Invalid email or password")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})

def registerVendor(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        vendor_form = VendorRegistrationForm(request.POST, request.FILES)

        if form.is_valid() and vendor_form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.role = User.RESTAURANT
            user.save()

            # Check if UserProfile exists; if not, create one
            user_profile, created = UserProfile.objects.get_or_create(user=user)

            # Create vendor and associate it with the UserProfile
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = user_profile  # Assign the existing or new UserProfile
            vendor.save()

            messages.success(request, "Vendor registered successfully! Please log in.")
            return redirect("login_view")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
        vendor_form = VendorRegistrationForm()

    return render(request, 'accounts/registerVendor.html', {'form': form, 'vendor_form': vendor_form})
