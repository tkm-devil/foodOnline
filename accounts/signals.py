from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import User, UserProfile
from vendor.models import Vendor
from foodOnline_main import settings

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    """Automatically create UserProfile when a new user registers."""
    if created:
        UserProfile.objects.create(user=instance)  # Create profile only when user is first created
        print("User Profile created!")

@receiver(post_save, sender=Vendor)
def send_verification_in_progress_email(sender, instance, created, **kwargs):
    """Send email after a vendor's account is activated to notify verification is in progress."""
    if created:  # If a new vendor is registered
        subject = "Your Vendor License Verification is in Progress!"
        message = (
            f"Hello {instance.vendor_name},\n\n"
            "Thank you for registering as a vendor on FoodOnline.\n"
            "Your account has been activated, and our team is currently verifying your license.\n\n"
            "We will notify you as soon as the verification is complete.\n\n"
            "Best regards,\n"
            "FoodOnline Team"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Replace with your sender email
            [instance.user.email],
            fail_silently=False,
        )

        print("Verification in progress email sent!")