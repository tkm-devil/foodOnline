from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    print(created)
    if created:
        UserProfile.objects.create(user=instance)
        print("User Profile created!")

    if not created:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)
            print("Profile was not found. Created a new one.")

        print("User Profile updated!")

@receiver(pre_save, sender=User)
def pre_save_user_receiver(sender, instance, **kwargs):
    print(instance.username, 'this user is beaing saved')

# post_save.connect(post_save_create_profile_receiver, sender=User)