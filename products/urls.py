# products/urls.py - CORRECTED to match the browser request

from django.urls import path
from .views import (
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    product_detail_api,
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('new/', ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # FIXED: This path now correctly matches /products/api/<pk>/
    path('api/<int:pk>/', product_detail_api, name='product_detail_api'),
]