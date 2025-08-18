from django.utils import timezone
from rest_framework import serializers
from .models import PushToken

class PushTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    deviceId = serializers.CharField(max_length=191, required=False, allow_blank=True, allow_null=True)
    platform = serializers.ChoiceField(
        choices=PushToken.Platform.choices, required=False, default=PushToken.Platform.WEB
    )
    created_at = serializers.DateTimeField(read_only=True, default_timezone=timezone.get_current_timezone())
    updated_at = serializers.DateTimeField(read_only=True, default_timezone=timezone.get_current_timezone())

class PushTokenDeleteSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
