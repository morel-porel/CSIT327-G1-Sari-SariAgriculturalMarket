from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Product
from .forms import ProductForm
from users.suspension_utils import can_user_add_edit_products

class VendorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated or user.role != 'VENDOR':
            return False
        
        # Check if vendor can add/edit products (not suspended)
        if not can_user_add_edit_products(user):
            return False
        
        return True
    
    def handle_no_permission(self):
        messages.error(self.request, "You cannot manage products while suspended or unverified.")
        return redirect('home')

class ProductListView(LoginRequiredMixin, VendorRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user).order_by('-created_at')

class ProductCreateView(LoginRequiredMixin, VendorRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.instance.vendor = self.request.user
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, VendorRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)

class ProductDeleteView(LoginRequiredMixin, VendorRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)

def product_detail_api(request, pk):
    try:
        product = Product.objects.select_related('vendor__vendorprofile').get(pk=pk)
        
        image_url = product.image.url if product.image else '/static/icons/placeholder.png'

        is_verified = False
        if hasattr(product.vendor, 'vendorprofile'):
            is_verified = product.vendor.vendorprofile.is_verified

        # Join categories list into a string for display
        category_display = ", ".join(product.category) if product.category else "N/A"

        data = {
            'id': product.pk,
            'name': product.name,
            'description': product.description,
            'price': f"₱{product.price}",
            'stock': product.stock,
            'category': category_display,
            'image_url': image_url,
            'shop_name': product.vendor.vendorprofile.shop_name,
            'seller_name': product.vendor.username,
            'vendor_user_id': product.vendor.pk,
            'is_verified': is_verified,
            'is_seasonal': product.is_seasonal,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

def product_list_api(request):
    """
    Advanced API endpoint for filtering products.
    """
    query = request.GET.get('q', '').strip()
    categories = request.GET.get('categories', '')
    regions = request.GET.get('regions', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    products_qs = Product.objects.all().select_related('vendor__vendorprofile').order_by('-created_at')
    
    # 1. Text Search
    if query:
        products_qs = products_qs.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    # 2. Category Filter (List) using ArrayField
    if categories:
        # Check if multiple categories are sent (separated by pipe |)
        # Use pipe as delimiter since category names contain commas
        if '|' in categories:
            category_list = [cat.strip() for cat in categories.split('|') if cat.strip()]
            if category_list:
                # Use Q objects with OR logic to show products that match ANY selected category
                category_filter = Q()
                for category in category_list:
                    category_filter |= Q(category__overlap=[category])
                products_qs = products_qs.filter(category_filter)
        else:
            # Single category filter (from home page buttons)
            category = categories.strip()
            if category:
                products_qs = products_qs.filter(category__overlap=[category])

    # 3. Location/Barangay Filter (List) - Filter by vendor's barangay
    if regions:
        region_list = [barangay.strip() for barangay in regions.split(',')]
        if region_list:
            # Filter products by vendor's barangay field using case-insensitive partial matching
            barangay_filter = Q()
            for barangay in region_list:
                barangay_filter |= Q(vendor__vendorprofile__barangay__icontains=barangay)
            products_qs = products_qs.filter(barangay_filter)

    # 4. Price Range Filter
    if min_price:
        try:
            products_qs = products_qs.filter(price__gte=float(min_price))
        except ValueError:
            pass 
            
    if max_price:
        try:
            products_qs = products_qs.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Build Response
    products_data = []
    for product in products_qs:
        vendor_profile = getattr(product.vendor, 'vendorprofile', None)
        shop_name = vendor_profile.shop_name if vendor_profile else 'Unknown Vendor'
        is_verified = vendor_profile.is_verified if vendor_profile else False 
        
        image_url = product.image.url if product.image else '/static/icons/placeholder.png'
        
        products_data.append({
            'id': product.pk,
            'name': product.name,
            'price': f"₱{product.price}",
            'image_url': image_url,
            'shop_name': shop_name,
            'vendor_id': product.vendor.pk,
            'is_verified': is_verified,
            'is_seasonal': product.is_seasonal,
        })
        
    return JsonResponse({'products': products_data})