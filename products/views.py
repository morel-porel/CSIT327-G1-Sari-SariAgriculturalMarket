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
    
def product_detail_api(request, pk): # Changed argument from product_id to pk
    """
    API endpoint to get product details as JSON.
    """
    try:
        # Use pk for lookup
        product = Product.objects.select_related('vendor__vendorprofile').get(pk=pk)
        
        # FIX 1: Correctly set the placeholder URL using static path if no image
        if product.image:
            image_url = product.image.url
        else:
            image_url = '/static/icons/placeholder.png' # Using the correct static path

        data = {
            'id': product.pk,
            'name': product.name,
            'description': product.description,
            'price': f"₱{product.price}", # Price already includes the currency symbol
            'stock': product.stock,
            'category': product.get_category_display(), # Gets the readable name
            'image_url': image_url,
            
            # FIX 2: Use key names expected by JavaScript
            'shop_name': product.vendor.vendorprofile.shop_name, 
            'seller_name': product.vendor.username,
            'vendor_user_id': product.vendor.pk, # The ID used to construct links
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        # Catch other errors, like missing vendorprofile 
        return JsonResponse({'error': f'Server error: Vendor profile data incomplete. {str(e)}'}, status=500)