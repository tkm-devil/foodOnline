from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from .utils import detectUser
from .forms import UserRegistrationForm, LoginForm
from .models import User, UserProfile
from .tokens import email_verification_token
from vendor.forms import VendorRegistrationForm

def send_verification_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    message = render_to_string('accounts/email_verification.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': email_verification_token.make_token(user),
    })
    send_mail(mail_subject, message, 'postmaster@sandboxf1f0b5d71e984c008eb4c1b9363536ab.mailgun.org', [user.email])

def registerUser(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in. Please logout to register a new account.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.is_active = False  # User must verify via email
            user.save()
            send_verification_email(request, user)
            messages.success(request, "A verification email has been sent. Please check your email to activate your account.")
            return redirect("login_view")
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
            user = form.save(commit=False)
            user.role = User.VENDOR
            user.is_active = False  # User must verify via email
            user.save()
            
            # Create UserProfile and Vendor
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = user_profile
            vendor.save()
            
            send_verification_email(request, user)
            messages.success(request, "A verification email has been sent. Please check your email to activate your account.")
            return redirect("login_view")
    else:
        form = UserRegistrationForm()
        vendor_form = VendorRegistrationForm()
    
    return render(request, 'accounts/registerVendor.html', {'form': form, 'vendor_form': vendor_form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect("login_view")
    else:
        messages.error(request, "Invalid activation link!")
        return redirect("home")

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect(detectUser(request.user))
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is not verified. Please check your email.")
                    return redirect("login_view")
                
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect(detectUser(user))
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
    return redirect(detectUser(request.user))

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
