# messaging/admin.py
from django.contrib import admin
from .models import Conversation, Message

# This code tells the admin site to show your models
admin.site.register(Conversation)
admin.site.register(Message)