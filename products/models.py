# products/models.py

from django.db import models
from users.models import CustomUser
from django.contrib.postgres.fields import ArrayField

class Product(models.Model):
    class Category(models.TextChoices):
        FRESH_PRODUCE = "Fresh Produce", "Fresh Produce"
        GRAINS_STAPLES = "Grains and Staples", "Grains and Staples"
        PACKAGED_GOODS = "Packaged Goods", "Packaged Goods"
        DAIRY_EGGS = "Dairy & Eggs", "Dairy & Eggs"
        MEAT_POULTRY_SEAFOOD = "Meat, Poultry and Seafood", "Meat, Poultry and Seafood"
        LOCAL_SPECIALTY = "Local & Specialty Products", "Local & Specialty Products"
        SERVICES = "Services", "Services"

    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    category = ArrayField(
    models.CharField(max_length=50, choices=Category.choices),
    default=list,
    blank=True
)
    
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name