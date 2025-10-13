from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ConsumerSignUpForm, VendorSignUpForm
from django.contrib.auth.decorators import login_required

def consumer_signup_view(request):
    if request.method == 'POST':
        form = ConsumerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') # Redirect to a home/dashboard page after success
    else:
        form = ConsumerSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def vendor_signup_view(request):
    if request.method == 'POST':
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') # Redirect home after signup
    else:
        form = VendorSignUpForm()
    return render(request, 'registration/vendor_signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'VENDOR':
                    return redirect('home') 
                elif user.role == 'CONSUMER':
                    return redirect('home')
                else: # Fallback for admins
                    return redirect('/admin/')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login') # Redirect back to the login page

def home_view(request):
    return render(request, 'home.html')

@login_required # This protects the page from logged-out users
def profile_view(request):
    # For now, we'll just pass the user's basic info to the template.
    # Later, we can add the ConsumerProfile model here.
    context = {
        'user': request.user
    }
    return render(request, 'pages/profile.html', context)