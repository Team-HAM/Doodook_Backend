from django.urls import path
from .views import (
    send_notification, 
    send_custom_notification, 
    send_user_notification,
    send_platform_notification
)

urlpatterns = [
    path('send/<int:notification_id>/', send_notification, name='alert-send'),
    path('send-custom/', send_custom_notification, name='alert-send-custom'),
    path('send-user/<int:user_id>/', send_user_notification, name='alert-send-user'),
    path('send-platform/<str:platform>/', send_platform_notification, name='alert-send-platform'),
]