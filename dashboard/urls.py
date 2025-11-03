# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # The main dashboard page
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    # The new page for verifying vendors
    path('vendors/', views.vendor_verification_view, name='vendor_verification'),
    path('reported-messages/', views.reported_messages_view, name='reported_messages'),
]