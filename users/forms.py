# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define placeholders for each field
        placeholders = {
            'username': 'Username',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
        
        # Remove the default help text and add placeholders
        for field_name, field in self.fields.items():
            # Remove the built-in help text
            field.help_text = None 
            
            # Add placeholder attribute if it's in our dictionary
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
                field.label = '' # Remove the label, since we have a placeholder

        # Special handling for the 'role' field if needed
        self.fields['role'].label = 'Select your role:' # We can keep a label for radio buttons