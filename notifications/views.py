# notifications/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import create_notification
from .models import Notification
from django.http import JsonResponse
from django.utils.timesince import timesince

def test_notification_view(request):
    if request.user.is_authenticated:
        create_notification(
            recipient=request.user,
            message="This is a test notification!",
            link="/about/"
        )
        messages.success(request, "Test notification created!")
    return redirect('home')

@login_required
def notification_list_view(request):
    """
    Displays all notifications for the logged-in user and marks them as read.
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    # We mark them as read when the user visits the full list page
    notifications.filter(is_read=False).update(is_read=True)

    context = {
        'notifications': notifications
    }
    
    return render(request, 'notifications/notification_list.html', context)

@login_required
def recent_notifications_api(request):
    """
    API to return the 5 most recent notifications for the navbar dropdown.
    """
    # Get 5 most recent
    recent = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    data = []
    for n in recent:
        data.append({
            'id': n.id,
            'message': n.message,
            'link': n.link if n.link else '#',
            'is_read': n.is_read,
            'time_since': timesince(n.timestamp).split(',')[0] + " ago" # simplified time
        })
    
    return JsonResponse({
        'notifications': data,
        'unread_count': unread_count
    })