from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, VendorProfile

class VendorProfileAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('user', 'shop_name', 'business_permit_number', 'is_verified')
    # Fields that can be edited directly from the list view
    list_editable = ('is_verified',)

# Register your models here.
admin.site.register(CustomUser, UserAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)