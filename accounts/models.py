from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ADMIN = "Admin"
    PROGRAM_MANAGER = "Program Manager"
    DATA_OFFICER = "Data Officer"
    VIEWER = "Viewer"
    ROLE_CHOICES = [
        (ADMIN, ADMIN),
        (PROGRAM_MANAGER, PROGRAM_MANAGER),
        (DATA_OFFICER, DATA_OFFICER),
        (VIEWER, VIEWER),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=VIEWER)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)

# Create your models here.
