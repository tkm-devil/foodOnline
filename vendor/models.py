from django.db import models
from accounts.models import User, UserProfile

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='vendor', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='vendor_profile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to='vendor/licenses/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['-created_at']

    def __str__(self):
        return self.vendor_name
