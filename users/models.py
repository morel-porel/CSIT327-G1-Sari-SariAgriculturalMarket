from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        VENDOR = "VENDOR", "Vendor"
        CONSUMER = "CONSUMER", "Consumer"

    # Add any common fields here, like a phone number
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CONSUMER)
    
class VendorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    shop_name = models.CharField(max_length=255)
    business_permit_number = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    contact_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='vendor_images/', blank=True, null=True)
    
    shop_description = models.TextField(blank=True, null=True) # Detailed Shop Information
    farming_practices = models.TextField(blank=True, null=True) # Farming Practices
    experience_years = models.IntegerField(blank=True, null=True) # Vendor Experience
    
    def __str__(self):
        return self.shop_name
