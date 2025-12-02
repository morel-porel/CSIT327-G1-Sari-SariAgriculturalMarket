from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, VendorProfile

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'username': 'Username',
            'email': 'Email Address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'password1': 'Password',
            'password2': 'Confirm Password',
            'shop_name': 'Shop Name',
            'business_permit_number': 'Business Permit Number',
        }
        
        for field_name, field in self.fields.items():
            field.help_text = None  
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
                field.label = '' 

class ConsumerSignUpForm(CustomUserCreationForm): 
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email')
    
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
        # Added first_name and last_name to fields
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Updated order to show names first
        self.field_order = [
            'first_name',
            'last_name',
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

class VendorStep1Form(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = [
            'shop_name',
            'contact_number',
            'pickup_address',
            'barangay',
            'city',
            'zip_code',
            'shop_description',
        ]
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Shop Name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0912 345 6789'}),
            'pickup_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'House/Unit No., Street Name'}),
            'barangay': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Barangay'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip Code'}),
            'shop_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell customers about your shop...'}),
        }

class VendorStep2UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class VendorStep2ProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['profile_image'] 
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
        }

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = '__all__'
        exclude = ['user', 'is_verified']

class ConsumerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'date_of_birth', 'avatar',
            'address', 'city', 'zip_code'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make phone_number not required to avoid validation issues with empty values
        self.fields['phone_number'].required = False
        # Ensure email is required
        self.fields['email'].required = True
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # If phone_number is empty, return None to avoid unique constraint issues
        if not phone_number or phone_number.strip() == '':
            return None
        
        # Check if another user has this phone number (excluding current user)
        if self.instance and self.instance.pk:
            # Only check for duplicates if the phone number has changed
            if self.instance.phone_number != phone_number:
                existing = CustomUser.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk)
                if existing.exists():
                    raise forms.ValidationError('This phone number is already in use.')
        else:
            # For new users, check if phone number exists
            existing = CustomUser.objects.filter(phone_number=phone_number)
            if existing.exists():
                raise forms.ValidationError('This phone number is already in use.')
        
        return phone_number