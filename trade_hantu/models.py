from django.db import models
from django.utils import timezone

# Create your models here.
class OAuthToken(models.Model):
    approval_key = models.CharField(max_length=286)
    def __str__(self):
        return self.approval_key

class AccessToken(models.Model):
    access_token = models.CharField(max_length=350)
    token_type = models.CharField(max_length=20)
    expires_in = models.IntegerField(default=0)
    expires_at = models.DateTimeField()
    is_expired = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.token_type} {self.access_token}"
    def is_token_expired(self):
        _is_expired = ( self.expires_at < timezone.now() )
        self.access_token_expired = _is_expired
        return _is_expired