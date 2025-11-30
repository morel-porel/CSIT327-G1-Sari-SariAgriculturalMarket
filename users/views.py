from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import (
    ConsumerSignUpForm, 
    VendorSignUpForm, 
    VendorProfileForm, 
    ConsumerProfileForm,
    VendorStep1Form,
    VendorStep2UserForm,
    VendorStep2ProfileForm
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import VendorProfile, CustomUser, SearchHistory
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction 
from notifications.utils import create_notification

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
        form.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        form.fields['password'].widget.attrs.update({'placeholder': 'Password'})
        form.fields['username'].label = ''
        form.fields['password'].label = ''
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('login')

def home_view(request):
    from products.models import Product
    products = Product.objects.all().select_related('vendor__vendorprofile').order_by('-created_at')
    context = {
        'products': products
    }
    return render(request, 'pages/home.html', context)

@login_required 
def profile_view(request):
    user = request.user
    
    profile_form = ConsumerProfileForm(instance=user)
    password_form = PasswordChangeForm(user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ConsumerProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile')
            else:
                messages.error(request, 'Please correct the errors in the password form.')

    context = {
        'form': profile_form,
        'password_form': password_form
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

@login_required
def become_vendor_view(request):
    user = request.user
    
    if user.role == 'VENDOR':
        return redirect('vendor_profile')

    try:
        profile = VendorProfile.objects.get(user=user)
    except VendorProfile.DoesNotExist:
        profile = VendorProfile(user=user)

    if profile.shop_name and profile.pickup_address and not profile.is_verified:
        return redirect('vendor_onboarding_success')

    return render(request, 'pages/become_vendor.html', {'status': 'new'})

@login_required
def vendor_onboarding_step1(request):
    user = request.user
    try:
        profile = VendorProfile.objects.get(user=user)
    except VendorProfile.DoesNotExist:
        profile = VendorProfile(user=user)

    if request.method == 'POST':
        form = VendorStep1Form(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('vendor_onboarding_step2') 
    else:
        form = VendorStep1Form(instance=profile)

    return render(request, 'pages/vendor_onboarding_step1.html', {'form': form})

@login_required
def vendor_onboarding_step2(request):
    user = request.user
    try:
        profile = VendorProfile.objects.get(user=user)
    except VendorProfile.DoesNotExist:
        return redirect('vendor_onboarding_step1')

    if request.method == 'POST':
        user_form = VendorStep2UserForm(request.POST, instance=user)
        profile_form = VendorStep2ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('vendor_onboarding_step3') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = VendorStep2UserForm(instance=user)
        profile_form = VendorStep2ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'pages/vendor_onboarding_step2.html', context)

@login_required
def vendor_onboarding_step3(request):
    user = request.user
    try:
        profile = VendorProfile.objects.get(user=user)
    except VendorProfile.DoesNotExist:
        return redirect('vendor_onboarding_step1')
    
    if request.method == 'POST':
        create_notification(
            recipient=request.user,
            message="Your vendor application has been submitted and is pending review.",
            link="#" 
        )

        messages.success(request, "Application Submitted Successfully!")
        return redirect('vendor_onboarding_success')

    context = {
        'profile': profile,
        'user': user
    }
    return render(request, 'pages/vendor_onboarding_step3.html', context)

@login_required
def vendor_onboarding_success(request):
    return render(request, 'pages/vendor_success.html')


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

        profile_image_url = profile.profile_image.url if profile.profile_image else '/static/icons/placeholder.png'

        data = {
            'shop_name': profile.shop_name,
            'description': profile.shop_description or 'No shop description provided.',
            'practices': profile.farming_practices or 'No farming practices detailed.',
            'experience': str(profile.experience_years) if profile.experience_years is not None else 'N/A', 
            'contact_number': profile.contact_number or 'N/A',
            'email': user.email,
            'is_verified': profile.is_verified,
            'business_permit_number': profile.business_permit_number or 'N/A',
            'profile_image_url': profile_image_url,
        }
        return JsonResponse(data)
    except Exception as e:
        print(f"Vendor API Crash for PK {pk}: {e}") 
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
    
@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        SearchHistory.objects.create(user=request.user, query=query)
        results = VendorProfile.objects.filter(
            Q(shop_name__icontains=query) |
            Q(shop_description__icontains=query)
        )

    recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'query': query,
        'results': results,
        'recent_searches': recent_searches,
    }
    return render(request, 'pages/search.html', context)

@login_required
def delete_search_history(request, history_id):
    history = get_object_or_404(SearchHistory, id=history_id, user=request.user)
    history.delete()
    messages.success(request, "Search entry deleted successfully.")
    return redirect('search')

@login_required
def clear_search_history(request):
    SearchHistory.objects.filter(user=request.user).delete()
    messages.success(request, "All search history cleared.")
    return redirect('search')