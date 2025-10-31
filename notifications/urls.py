from django.urls import path
from . import views

urlpatterns = [
    path('test-notification/', views.test_notification_view, name='test_notification'),
]