# pages/views.py

from django.shortcuts import render
from products.models import Product # Import the Product model
from django.contrib.auth.decorators import login_required

def about_us_view(request):
    # This view's only job is to render the 'about.html' template.
    return render(request, 'pages/about.html')

def home_view(request):
    products = Product.objects.all().select_related('vendor__vendorprofile').order_by('-created_at') # Get all products
    context = {
        'products': products
    }
    return render(request, 'pages/home.html', context)

@login_required
def become_vendor_view(request):
    """
    A page that informs consumers how to become a vendor
    before sending them to the vendor signup form.
    """
    return render(request, 'pages/become_vendor.html')