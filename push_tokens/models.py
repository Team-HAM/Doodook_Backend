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
    is_active = models.BooleanField(default=True)  # 토큰 활성화 상태
    revoked_at = models.DateTimeField(null=True, blank=True)  # 토큰 폐기 시간
    app_version = models.CharField(max_length=20, null=True, blank=True)  # 앱 버전
    os_version = models.CharField(max_length=20, null=True, blank=True)  # OS 버전
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user", "platform"])]
        indexes = [models.Index(fields=["is_active"])]  # 활성 토큰 조회 최적화

    def __str__(self):
        return f"{self.user.username} - {self.platform} ({self.device_id})"
