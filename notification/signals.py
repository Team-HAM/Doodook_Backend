# notification/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from alert.utils import send_push_to_all  # 이미 있는 util 재사용

@receiver(post_save, sender=Notification)
def send_push_on_create(sender, instance, created, **kwargs):
    if created and not instance.is_sent:
        success = send_push_to_all(instance.title, instance.content)
        if success:
            instance.is_sent = True
            instance.save(update_fields=["is_sent"])
