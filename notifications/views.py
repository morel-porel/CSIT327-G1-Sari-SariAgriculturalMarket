# notifications/views.py (Corrected)
from django.shortcuts import render, redirect
from django.contrib import messages
# FIX: Import the missing login_required decorator
from django.contrib.auth.decorators import login_required 
from .utils import create_notification
from .models import Notification # Assuming this import was added previously

def test_notification_view(request):
    if request.user.is_authenticated:
        create_notification(
            recipient=request.user,
            message="This is a test notification!",
            link="/about/"
        )
        messages.success(request, "Test notification created!")
    return redirect('home')

# The view where the NameError occurred:
@login_required
def notification_list_view(request):
    """
    Displays all notifications for the logged-in user and marks them as read.
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    notifications.filter(is_read=False).update(is_read=True)

    context = {
        'notifications': notifications
    }
    
    return render(request, 'notifications/notification_list.html', context)