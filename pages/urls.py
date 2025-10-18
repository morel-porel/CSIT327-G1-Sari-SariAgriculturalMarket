# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about_us_view, name='about'),
    path('', views.home_view, name='home'),
    path('become-vendor/', views.become_vendor_view, name='become_vendor'),
]