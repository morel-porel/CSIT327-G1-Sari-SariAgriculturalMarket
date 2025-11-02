# notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # The new root path for the notifications app
    path('', views.notification_list_view, name='notification_list'), 
    
    path('test-notification/', views.test_notification_view, name='test_notification'),
]