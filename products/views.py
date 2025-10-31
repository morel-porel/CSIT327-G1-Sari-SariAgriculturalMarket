# products/views.py

from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product
from .forms import ProductForm

class VendorRequiredMixin(UserPassesTestMixin):
    """Ensures that the logged-in user is a vendor."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'VENDOR'

class ProductListView(LoginRequiredMixin, VendorRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Only show products belonging to the logged-in vendor
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
        # Ensure vendor can only edit their own products
        return Product.objects.filter(vendor=self.request.user)

class ProductDeleteView(LoginRequiredMixin, VendorRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)
    
def product_detail_api(request, product_id):
    """
    API endpoint to get product details as JSON.
    """
    try:
        product = Product.objects.select_related('vendor__vendorprofile').get(id=product_id)
        
        if product.image:
            image_url = product.image.url
        else:
            # You might want a placeholder image URL here
            image_url = ''

        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': f"₱{product.price}",
            'stock': product.stock,
            'category': product.get_category_display(), # Gets the readable name
            'image_url': image_url,
            'vendor_name': product.vendor.vendorprofile.shop_name,
            'vendor_chat_url': f"/messages/start/{product.vendor.id}/"
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)