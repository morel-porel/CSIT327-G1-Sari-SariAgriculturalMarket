# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, VendorProfile

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'username': 'Username',
            'email': 'Email Address',
            'password1': 'Password',
            'password2': 'Confirm Password',
            'shop_name': 'Shop Name',
            'business_permit_number': 'Business Permit Number',
        }
        
        for field_name, field in self.fields.items():
            field.help_text = None  # Remove the default help text
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
                field.label = ''  # Remove the label


class ConsumerSignUpForm(CustomUserCreationForm): 
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.CONSUMER
        if commit:
            user.save()
        return user

class VendorSignUpForm(CustomUserCreationForm): 
    shop_name = forms.CharField(max_length=255, required=True)
    business_permit_number = forms.CharField(max_length=100, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_order = [
            'username', 
            'email', 
            'shop_name', 
            'business_permit_number', 
            'password1', 
            'password2'
        ]
        

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.VENDOR
        if commit:
            user.save()
            VendorProfile.objects.create(
                user=user,
                shop_name=self.cleaned_data.get('shop_name'),
                business_permit_number=self.cleaned_data.get('business_permit_number')
            )
        return user
    
class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['shop_name', 'business_permit_number', 'contact_number', 'profile_image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'shop_name': 'Shop Name',
            'business_permit_number': 'Business Permit Number',
            'contact_number': 'Contact Number',
            'profile_image': 'Profile Image',
        }
        
        for field_name, field in self.fields.items():
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
                field.label = ''  # Remove the label