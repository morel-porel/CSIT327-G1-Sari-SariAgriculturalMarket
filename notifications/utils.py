# notifications/utils.py
from .models import Notification

def create_notification(recipient, message, link=None):
    """
    A simple helper function to create a new notification.
    This is what the messaging app will call.
    """
    Notification.objects.create(
        recipient=recipient,
        message=message,
        link=link
    )