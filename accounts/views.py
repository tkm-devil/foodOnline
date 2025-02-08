from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm, OTPVerificationForm
from .models import User, UserProfile
from .utils import detectUser
from vendor.forms import VendorRegistrationForm

# Register User (With OTP Verification)
def registerUser(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in. Please logout to register a new account.')
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.is_active = False  # User must verify via OTP
            user.save()
            User.objects.send_otp_email(user.email, user.otp)  # Send OTP after saving

            request.session['email'] = user.email  # Store email in session for OTP verification
            messages.success(request, "An OTP has been sent to your email. Verify to activate your account.")
            return redirect("verify_otp_view")  # Redirect to OTP verification page

    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/registerUser.html', {'form': form})

# Register Vendor (With OTP Verification)
def registerVendor(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in. Please logout to register a new account.')
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        vendor_form = VendorRegistrationForm(request.POST, request.FILES)

        if form.is_valid() and vendor_form.is_valid():
            user = form.save(commit=False)
            user.role = User.VENDOR
            user.is_active = False  # User must verify via OTP
            user.save()
            User.objects.send_otp_email(user.email, user.otp)  # Send OTP after saving

            # Create UserProfile and Vendor
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = user_profile
            vendor.save()

            request.session['email'] = user.email
            messages.success(request, "An OTP has been sent to your email. Verify to activate your account.")
            return redirect("verify_otp_view")  # Redirect to OTP verification page

    else:
        form = UserRegistrationForm()
        vendor_form = VendorRegistrationForm()

    return render(request, 'accounts/registerVendor.html', {'form': form, 'vendor_form': vendor_form})

# OTP Verification View (Using Form)
def verify_otp(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, "Session expired. Please register again.")
        return redirect("registerUser")

    user = get_object_or_404(User, email=email)

    if request.method == "POST":
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data["otp"]

            if user.check_otp(otp):
                messages.success(request, "Email verified successfully! You can now log in.")
                return redirect("login_view")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
    else:
        form = OTPVerificationForm()

    return render(request, "accounts/verify_otp.html", {"form": form})

# Login with OTP check
def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect(detectUser(request.user))  # Redirect to the correct dashboard

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is not verified. Please check your email for OTP.")
                    request.session['email'] = user.email  # Store email for OTP retry
                    return redirect("verify_otp_view")  # Redirect to OTP verification

                login(request, user)
                messages.success(request, "Login successful!")
                return redirect(detectUser(user))  # Redirect to their respective dashboard
            else:
                messages.error(request, "Invalid email or password")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})

# Logout
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. Login again to continue.")
    return redirect('login_view')

# Redirect to correct dashboard
@login_required
def dashboard(request):
    return redirect(detectUser(request.user))

# Customer Dashboard
@login_required
def customerDashboard(request):
    if request.user.role != User.CUSTOMER:
        messages.error(request, "Unauthorized access! You are not a customer.")
        return redirect("home")
    return render(request, "accounts/customerDashboard.html")

# Vendor Dashboard
@login_required
def vendorDashboard(request):
    if request.user.role != User.VENDOR:
        messages.error(request, "Unauthorized access! You are not a vendor.")
        return redirect("home")
    return render(request, "accounts/vendorDashboard.html")
