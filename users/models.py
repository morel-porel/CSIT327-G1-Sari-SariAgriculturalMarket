# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        VENDOR = "VENDOR", "Vendor"
        CONSUMER = "CONSUMER", "Consumer"

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
    
    shop_description = models.TextField(blank=True, null=True) 
    farming_practices = models.TextField(blank=True, null=True) 
    experience_years = models.IntegerField(blank=True, null=True) 

    # --- NEW FIELDS FOR STEP 1 (ADDRESS) ---
    pickup_address = models.TextField(blank=True, null=True, help_text="Street Address / Landmark")
    barangay = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.shop_name
    
class SearchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='search_histories')
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched '{self.query}'"

class LoyaltyProfile(models.Model):
    RANK_CHOICES = (
        ('Bronze', 'Bronze'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    rank = models.CharField(max_length=10, choices=RANK_CHOICES, default='Bronze')

    def update_rank(self):
        """Automatically update rank based on points."""
        if self.points >= 100:
            self.rank = 'Gold'
        elif self.points >= 50:
            self.rank = 'Silver'
        else:
            self.rank = 'Bronze'
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.rank}"
    
def create_loyalty_profile(sender, instance, created, **kwargs):
    if created:
        LoyaltyProfile.objects.create(user=instance)