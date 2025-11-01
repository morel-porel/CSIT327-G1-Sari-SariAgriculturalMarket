from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Product
from .forms import ProductForm

class VendorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'VENDOR'

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
        
        if product.image:
            image_url = product.image.url
        else:
            image_url = '/static/icons/placeholder.png'

        data = {
            'id': product.pk,
            'name': product.name,
            'description': product.description,
            'price': f"₱{product.price}",
            'stock': product.stock,
            'category': product.get_category_display(),
            'image_url': image_url,
            'shop_name': product.vendor.vendorprofile.shop_name,
            'seller_name': product.vendor.username,
            'vendor_user_id': product.vendor.pk,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

def product_list_api(request):
    """
    API endpoint to list products with optional filtering by category.
    Accessed via /my-products/api/list/?category=Category Name
    """
    category_filter = request.GET.get('category')
    
    products_qs = Product.objects.all().select_related('vendor__vendorprofile').order_by('-created_at')
    
    if category_filter and category_filter != 'all':
        # Filter by the category field using the exact name
        products_qs = products_qs.filter(category=category_filter)
        
    products_data = []
    for product in products_qs:
        # Check if vendorprofile exists before accessing it
        vendor_profile = getattr(product.vendor, 'vendorprofile', None)
        shop_name = vendor_profile.shop_name if vendor_profile else 'Unknown Vendor'
        
        image_url = product.image.url if product.image else '/static/icons/placeholder.png'
        
        products_data.append({
            'id': product.pk,
            'name': product.name,
            'price': f"₱{product.price}",
            'image_url': image_url,
            'shop_name': shop_name,
            'vendor_id': product.vendor.pk,
        })
        
    return JsonResponse({'products': products_data})