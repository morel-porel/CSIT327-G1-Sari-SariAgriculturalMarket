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

def create_moderation_warning(recipient, message_content_snippet):
    """
    Helper function for moderation warnings.
    """
    # Create a notification that the reported user will see in their notification list
    Notification.objects.create(
        recipient=recipient,
        message=f"Warning: Your message, '{message_content_snippet}', was flagged for inappropriate content.",
        link=None
    )