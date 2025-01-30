from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
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
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    RESTAURANT = 1
    CUSTOMER = 2

    USER_TYPE_CHOICES = (
        (RESTAURANT, "Restaurant"),
        (CUSTOMER, "Customer"),
    )

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)  # Users are active by default
    is_staff = models.BooleanField(default=False)  # Regular users are not staff
    is_superuser = models.BooleanField(default=False)  # Regular users are not superusers

    objects = UserManager()

    USERNAME_FIELD = "email"  # Authentication will use email instead of username
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]  # Required for createsuperuser

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        db_table = "custom_user"
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        """Return True if user has a specific permission (for Django admin)."""
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        """Return True if user has permissions to view the app (for Django admin)."""
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
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-created_at"]
        db_table = "user_profile"

    def __str__(self):
        return self.user.email
