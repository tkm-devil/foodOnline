from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .forms import UserRegistrationForm, LoginForm
from .models import User

# Create your views here.

def registerUser(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login_view')
        else:
            messages.error(request, 'Please correct the error below.') # Display general error message
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/registerUser.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=email, password=password)  # Auth via email
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("home")  # Redirect to home or dashboard
            else:
                messages.error(request, "Invalid email or password")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})
