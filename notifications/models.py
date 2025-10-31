# notifications/models.py
from django.db import models
from users.models import CustomUser

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    # A generic link to where the notification should take the user
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message}"

    class Meta:
        ordering = ['-timestamp'] # Show newest notifications first