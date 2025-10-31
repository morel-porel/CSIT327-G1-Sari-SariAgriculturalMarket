# notifications/context_processors.py
from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        # Fetch all notifications for the user that are not read
        notifications = request.user.notifications.filter(is_read=False)
        return {'unread_notifications': notifications}
    return {}