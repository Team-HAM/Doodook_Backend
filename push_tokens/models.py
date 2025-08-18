# push_tokens/models.py
from django.conf import settings
from django.db import models

class PushToken(models.Model):
    class Platform(models.TextChoices):
        WEB = "web", "web"
        ANDROID = "android", "android"
        IOS = "ios", "ios"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="push_tokens")
    token = models.CharField(max_length=255, unique=True)
    device_id = models.CharField(max_length=191, null=True, blank=True)
    platform = models.CharField(max_length=10, choices=Platform.choices, default=Platform.WEB)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user", "platform"])]
