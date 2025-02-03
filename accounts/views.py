from django.shortcuts import redirect, render
from django.http import HttpResponse
from .forms import UserRegistrationForm
from .models import User

# Create your views here.

def registerUser(request):
    if request.method == 'POST':
        print(request.POST)
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.save()
            return redirect('registerUser')
    else:
        form = UserRegistrationForm()
    context = {
        'form': form
    } 
    return render(request, 'accounts/registerUser.html', context)