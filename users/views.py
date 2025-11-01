from django.shortcuts import render, redirect, get_object_or_404 # get_object_or_404 is now grouped
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ConsumerSignUpForm, VendorSignUpForm, VendorProfileForm, ConsumerProfileForm # Group all forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
# from django.db.models import F # Removed, as it's not used

from .models import VendorProfile, CustomUser # Single, comprehensive model import

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
    messages.info(request, "You have been successfully logged out.") # Optional: add a message
    return redirect('login')

def home_view(request):
    return render(request, 'home.html')

@login_required # This protects the page from logged-out users
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = ConsumerProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile') # Redirect to the same page to show the changes
    else:
        form = ConsumerProfileForm(instance=user)

    # For now, we'll just pass the user's basic info to the template.
    # Later, we can add the ConsumerProfile model here.
    context = {
        'form': form
    }
    return render(request, 'pages/consumer_profile.html', context)

@login_required 
def vendor_profile_view(request):
    # Security check: Ensure the user is actually a vendor.
    if request.user.role != 'VENDOR':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    profile = get_object_or_404(VendorProfile, user=request.user)

    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('vendor_profile') 
    else:
        form = VendorProfileForm(instance=profile)

    return render(request, 'pages/vendor_profile.html', {'form': form})

def consumer_vendor_profile_view(request, vendor_id):
    """
    Displays the public-facing vendor profile to a consumer/public user.
    """
    # Fetch the vendor's CustomUser and the associated VendorProfile
    vendor_user = get_object_or_404(CustomUser, pk=vendor_id, role=CustomUser.Role.VENDOR)
    profile = get_object_or_404(VendorProfile, user=vendor_user)
    
    context = {
        'vendor_user': vendor_user,
        'profile': profile,
    }
    # Renders the new public profile template
    return render(request, 'pages/vendor_public_profile.html', context)