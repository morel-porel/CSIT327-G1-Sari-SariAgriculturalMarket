# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about_us_view, name='about'),
    path('', views.home_view, name='home'),
    path('become-vendor/', views.become_vendor_view, name='become_vendor'),

    path('search/', views.search_view, name='search'),
    path('search/delete/<int:history_id>/', views.delete_search_history, name='delete_search_history'),
    path('search/clear/', views.clear_search_history, name='clear_search_history'),
]