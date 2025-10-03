# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about_us_view, name='about'),
]