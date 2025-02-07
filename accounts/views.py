from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from vendor.forms import VendorRegistrationForm
from .forms import UserRegistrationForm, LoginForm
from .models import User, UserProfile
from .utils import detectUser

# Create your views here.

def registerUser(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in. Please logout to register a new account.')
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.save()
            request.session['registration_success'] = 'Account created successfully! Please login.'
            return redirect('login_view')  # Redirect to login instead of registerUser
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/registerUser.html', {'form': form})

def registerVendor(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in. Please logout to register a new account.')
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        vendor_form = VendorRegistrationForm(request.POST, request.FILES)

        if form.is_valid() and vendor_form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.role = User.VENDOR
            user.save()

            # Check if UserProfile exists; if not, create one
            user_profile, created = UserProfile.objects.get_or_create(user=user)

            # Create vendor and associate it with the UserProfile
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = user_profile  # Assign the existing or new UserProfile
            vendor.save()

            request.session['registration_success'] = 'Vendor registered successfully! Please log in.'
            return redirect("login_view")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
        vendor_form = VendorRegistrationForm()

    return render(request, 'accounts/registerVendor.html', {'form': form, 'vendor_form': vendor_form})

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect(detectUser(request.user))  # Redirect to the correct dashboard

    registration_success = request.session.pop("registration_success", None)
    if registration_success:
        messages.success(request, registration_success)

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)  # Auth via email
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect(detectUser(user))  # Redirect to their respective dashboard
            else:
                messages.error(request, "Invalid email or password")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. Login again to continue.")
    return redirect('login_view')

@login_required
def dashboard(request):
    redirect_url = detectUser(request.user)  # Get correct dashboard URL
    return redirect(redirect_url)  # Redirect to the appropriate dashboard

@login_required
def customerDashboard(request):
    if request.user.role != User.CUSTOMER:
        messages.error(request, "Unauthorized access! You are not a customer.")
        return redirect("home") 
    return render(request, "accounts/customerDashboard.html")

@login_required
def vendorDashboard(request):
    if request.user.role != User.VENDOR:
        messages.error(request, "Unauthorized access! You are not a vendor.")
        return redirect("home")
    return render(request, "accounts/vendorDashboard.html")
