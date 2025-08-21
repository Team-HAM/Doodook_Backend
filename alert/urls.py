from django.urls import path
from .views import send_notification

urlpatterns = [
    path('send/<int:notification_id>/', send_notification, name='alert-send'),
]