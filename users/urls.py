# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication URLs ---
    path('signup/', views.consumer_signup_view, name='signup'),
    path('signup/vendor/', views.vendor_signup_view, name='vendor_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Profile URLs ---
    path('consumer_profile/', views.profile_view, name='profile'),
    path('vendor_profile/', views.vendor_profile_view, name='vendor_profile'),

    path('api/vendor/<int:pk>/', views.vendor_detail_api, name='vendor_detail_api'),
]