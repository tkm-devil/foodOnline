import base64
import uuid
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.urls import reverse
from foodOnline_main import settings

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
            verification_token=str(uuid.uuid4()),
        )
        user.set_password(password)
        user.is_active = False  # Account will only be active after verification
        user.save(using=self._db)

        # Send Verification Email
        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        subject = "Email Verification"

        # Encode user.pk in base64
        uidb64 = base64.urlsafe_b64encode(str(user.pk).encode()).decode()

        verification_url = f"{settings.FRONTEND_URL}{reverse('activate', args=[uidb64, user.verification_token])}"
        print("Verification URL:", verification_url)
        message = f"Click the link to verify your email: {verification_url}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    VENDOR = 1
    CUSTOMER = 2

    USER_TYPE_CHOICES = (
        (VENDOR, "Vendor"),
        (CUSTOMER, "Customer"),
    )

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=True, null=True, unique=True, region="IN")
    role = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=False, help_text="User needs to verify email before activation.")
    is_staff = models.BooleanField(default=False, help_text="Allows the user to access the admin panel.")
    is_superuser = models.BooleanField(default=False, help_text="Grants all permissions to the user.")

    verification_token = models.CharField(max_length=64, unique=True, default=uuid.uuid4, help_text="Unique token for email verification.")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        db_table = "custom_user"

    def __str__(self):
        return self.email
    
    def generate_verification_token(self):
        self.verification_token = str(uuid.uuid4())
        if self.pk:  # If user already exists in database
            self.save(update_fields=["verification_token"])
        else:  # If new user
            self.save()

    def get_role(self):
        return dict(self.USER_TYPE_CHOICES).get(self.role, "None")

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="user/profile_pictures/", blank=True, null=True)
    cover_picture = models.ImageField(upload_to="user/cover_pictures/", blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-created_at"]
        db_table = "user_profile"

    def __str__(self):
        return self.user.email
