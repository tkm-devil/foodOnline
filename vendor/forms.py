from django import forms
from .models import Vendor

class VendorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
        widgets = {
            'vendor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor_license': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }