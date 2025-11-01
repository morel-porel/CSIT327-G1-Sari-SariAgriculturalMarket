# notifications/utils.py
from .models import Notification

def create_notification(recipient, message, link=None):
    """
    A simple helper function to create a new notification.
    The link should be the URL path, e.g., /messages/1/
    """
    Notification.objects.create(
        recipient=recipient,
        message=message,
        link=link
    )