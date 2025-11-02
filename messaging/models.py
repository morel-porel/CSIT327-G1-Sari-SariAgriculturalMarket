# messaging/models.py
from django.db import models
from users.models import CustomUser # We import your CustomUser model

# Define choices for the moderation action field
MODERATION_ACTION_CHOICES = (
    ('none', 'No Action Taken'),
    ('warn', 'Warn User'),
    ('delete', 'Delete Message'),
    ('ban', 'Ban User'),
)

class Conversation(models.Model):
    """
    A conversation between two or more users.
    """
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Helper to show participants in admin
        return f"Conversation {self.id} between: " + ", ".join([user.username for user in self.participants.all()])

class Message(models.Model):
    """
    A single message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    text_content = models.TextField(blank=True, null=True)
    
    # This field handles Task 1.7.1.4 (Add media file upload feature)
    media_file = models.FileField(upload_to='chat_media/', blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # NEW FIELD: To flag message as deleted/hidden by a moderator (Soft Delete)
    is_moderator_deleted = models.BooleanField(default=False) 

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['timestamp'] # Show oldest messages first in a chat window

# NEW MODEL: MessageReport (for Admin Moderation Tools)
class MessageReport(models.Model):
    """
    Model to store a report against a specific Message instance.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='reported_messages') 
    
    # Task: Add report message feature
    reason = models.TextField(help_text="Reason given by the user for reporting the message.")
    reported_at = models.DateTimeField(auto_now_add=True)
    
    # Moderation fields
    is_resolved = models.BooleanField(default=False)
    moderation_action = models.CharField(
        max_length=50,
        choices=MODERATION_ACTION_CHOICES,
        default='none',
        help_text="The final action taken by the admin."
    )
    # The admin user who took the action.
    moderator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reports')
    resolution_notes = models.TextField(null=True, blank=True, help_text="Internal notes on the resolution.")
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        snippet = self.message.text_content[:50] + '...' if self.message.text_content else '[Media File]'
        return f"Report {self.id} on '{snippet}' by {self.reporter.username}"

    class Meta:
        verbose_name = "Message Report"
        verbose_name_plural = "Message Reports"
        # Prevents the same user from spam-reporting the same message twice
        unique_together = ('message', 'reporter')