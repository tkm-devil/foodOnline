from django import forms
from .models import Vendor, MenuItem

class VendorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
        widgets = {
            'vendor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor_license': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }