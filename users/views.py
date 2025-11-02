from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ConsumerSignUpForm, VendorSignUpForm, VendorProfileForm, ConsumerProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import VendorProfile, CustomUser
from django.http import JsonResponse # CRITICAL: Ensure JsonResponse is imported

def consumer_signup_view(request):
    if request.method == 'POST':
        form = ConsumerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = ConsumerSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def vendor_signup_view(request):
    if request.method == 'POST':
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
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
                if user.is_superuser:
                    return redirect('admin_dashboard')
                if user.role == 'VENDOR':
                    return redirect('home') 
                elif user.role == 'CONSUMER':
                    return redirect('home')
                else: 
                    return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('login')

def home_view(request):
    # This view likely needs to fetch products, but is fine as is for now
    return render(request, 'home.html')

@login_required 
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = ConsumerProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = ConsumerProfileForm(instance=user)

    context = {
        'form': form
    }
    return render(request, 'pages/consumer_profile.html', context)

@login_required
def vendor_profile_view(request):
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
    vendor_user = get_object_or_404(CustomUser, pk=vendor_id, role=CustomUser.Role.VENDOR)
    profile = get_object_or_404(VendorProfile, user=vendor_user)
    
    context = {
        'vendor_user': vendor_user,
        'profile': profile,
    }
    return render(request, 'pages/vendor_public_profile.html', context)

def vendor_detail_api(request, pk):
    try:
        user = get_object_or_404(CustomUser, pk=pk, role='VENDOR')
        profile = get_object_or_404(VendorProfile, user=user) 

        # Handle optional image field
        profile_image_url = profile.profile_image.url if profile.profile_image else '/static/icons/placeholder.png'

        data = {
            'shop_name': profile.shop_name,
            'description': profile.shop_description or 'No shop description provided.',
            'practices': profile.farming_practices or 'No farming practices detailed.',
            
            # CRITICAL FIX: Safely convert nullable IntegerField to string
            'experience': str(profile.experience_years) if profile.experience_years is not None else 'N/A', 
            
            'contact_number': profile.contact_number or 'N/A',
            'email': user.email,
            'is_verified': profile.is_verified,
            'business_permit_number': profile.business_permit_number or 'N/A',
            'profile_image_url': profile_image_url,
        }
        return JsonResponse(data)
    except Exception as e:
        # This will catch any unexpected errors and return a 500, with a message for the console
        print(f"Vendor API Crash for PK {pk}: {e}") 
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)