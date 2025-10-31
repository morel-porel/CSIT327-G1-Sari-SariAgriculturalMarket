# products/urls.py

from django.urls import path
from .views import (
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    product_detail_api,  # <-- 1. Add the function to your import list
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('new/', ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # 2. Remove the "views." prefix so it uses the function directly
    path('api/detail/<int:product_id>/', product_detail_api, name='product_detail_api'),
]