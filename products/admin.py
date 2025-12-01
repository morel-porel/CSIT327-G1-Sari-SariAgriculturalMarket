# products/admin.py

from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    """Customizes the display of the Product model in the admin panel."""
    list_display = ('name', 'vendor', 'price', 'stock', 'created_at')
    list_filter = ('vendor',) 
    search_fields = ('name', 'description')

admin.site.register(Product, ProductAdmin)