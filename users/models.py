from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        VENDOR = "VENDOR", "Vendor"
        CONSUMER = "CONSUMER", "Consumer"

    # Add any common fields here, like a phone number
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    
    # This is the crucial field for role-based access
    role = models.CharField(max_length=50, choices=Role.choices)
