# products/forms.py

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    # Use MultipleChoiceField with CheckboxSelectMultiple widget
    category = forms.MultipleChoiceField(
        choices=Product.Category.choices,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'category-checkboxes'}),
        required=True
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock', 'image', 'is_seasonal']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            # category widget is overridden above
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock Quantity'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_seasonal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }