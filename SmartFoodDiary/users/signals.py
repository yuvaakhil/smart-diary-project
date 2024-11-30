from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Creates or updates the associated UserProfile when a User instance is created or updated.
    """
    if created:
        # Create the profile if it doesn't exist
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Update the profile if it already exists
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()

@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    """
    Deletes the associated UserProfile when a User instance is deleted.
    """
    try:
        profile = UserProfile.objects.get(user=instance)
        profile.delete()
    except UserProfile.DoesNotExist:
        pass

@receiver(post_delete, sender=UserProfile)
def delete_user_on_profile_delete(sender, instance, **kwargs):
    """
    Deletes the associated User when a UserProfile instance is deleted.
    """
    try:
        user = instance.user
        user.delete()  # Delete the related User
    except User.DoesNotExist:
        pass  # If no User exists, do nothing