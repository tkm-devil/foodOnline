from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'role')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)