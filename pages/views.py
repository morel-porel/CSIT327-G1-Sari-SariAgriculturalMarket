# pages/views.py

from django.shortcuts import render
from products.models import Product # Import the Product model

def about_us_view(request):
    # This view's only job is to render the 'about.html' template.
    return render(request, 'pages/about.html')

def home_view(request):
    products = Product.objects.all().order_by('-created_at') # Get all products
    context = {
        'products': products
    }
    return render(request, 'pages/home.html', context)