# notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list_view, name='notification_list'),
    path('test-notification/', views.test_notification_view, name='test_notification'),
    
    # New API URL
    path('api/recent/', views.recent_notifications_api, name='recent_notifications_api'),
]