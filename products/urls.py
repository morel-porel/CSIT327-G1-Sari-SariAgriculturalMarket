# products/urls.py - UPDATED

from django.urls import path
from .views import (
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    product_detail_api,
    product_list_api, # Added new API view
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('new/', ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # Existing API for product detail modal
    path('api/<int:pk>/', product_detail_api, name='product_detail_api'),
    
    # NEW API for filtering the product list (AJAX)
    path('api/list/', product_list_api, name='product_list_api'),
]