from django.db import models
from accounts.models import User, UserProfile
from foodOnline_main import settings
from django.core.mail import send_mail
from django.utils.html import format_html

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
    
    def save(self, *args, **kwargs):
        # Check if instance is new or if is_verified changed
        if self.pk:  # If vendor already exists
            old_instance = Vendor.objects.filter(pk=self.pk).first()
            if old_instance and not old_instance.is_verified and self.is_verified:
                # Send verification success email when is_verified changes from False to True
                self.send_verification_success_email()

        super().save(*args, **kwargs)

    def send_verification_success_email(self):
        """Send email to vendor when admin verifies their account."""
        subject = "Your Vendor Account is Now Verified!"
        message = (
            f"Hello {self.vendor_name},\n\n"
            "Great news! Your vendor account has been successfully verified. 🎉\n"
            "You can now start listing and selling your products on our platform.\n\n"
            "If you have any questions, feel free to contact support.\n\n"
            "Best regards,\n"
            "FoodOnline Team"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Replace with your sender email
            [self.user.email],
            fail_silently=False,
        )
