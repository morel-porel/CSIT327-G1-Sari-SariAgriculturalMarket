# messaging/models.py
from django.db import models
from users.models import CustomUser # We import your CustomUser model

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

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['timestamp'] # Show oldest messages first in a chat window