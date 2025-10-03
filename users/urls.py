# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.consumer_signup_view, name='signup'),
    path('signup/vendor/', views.vendor_signup_view, name='vendor_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]