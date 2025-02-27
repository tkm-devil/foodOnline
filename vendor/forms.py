from django import forms
from .models import Vendor, VendorMenuItem


# ✅ Vendor Registration Form
class VendorRegistrationForm(forms.ModelForm):
    """Form for vendors to register and submit their details."""
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
        widgets = {
            'vendor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter vendor name'}),
            'vendor_license': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ✅ Vendor Menu Item Form
class VendorMenuItemForm(forms.ModelForm):
    """Form for vendors to add/edit menu items."""
    class Meta:
        model = VendorMenuItem
        fields = ['name', 'description', 'price', 'image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter item description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        """Ensure a vendor does not add duplicate menu items."""
        name = self.cleaned_data.get('name')
        vendor = self.instance.vendor if self.instance.pk else None  # Get the vendor if updating
        if vendor and VendorMenuItem.objects.filter(vendor=vendor, name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("You already have an item with this name in your menu.")
        return name
