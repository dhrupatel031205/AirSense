from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    NOTIFICATION_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notifications'),
        ('all', 'All Methods'),
        ('none', 'No Notifications'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    health_conditions = models.TextField(blank=True, help_text="Any health conditions related to air quality")
    notification_preferences = models.CharField(
        max_length=10, 
        choices=NOTIFICATION_CHOICES, 
        default='email'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Ensure a UserProfile exists for every User. Use get_or_create to be idempotent
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Only attempt to save the related UserProfile if it exists
    try:
        profile = getattr(instance, 'userprofile', None)
        if profile is not None:
            profile.save()
    except Exception:
        # In case of any unexpected error, create a profile to recover gracefully
        try:
            UserProfile.objects.get_or_create(user=instance)
        except Exception:
            # If even creation fails, we don't want to crash user save flow
            pass