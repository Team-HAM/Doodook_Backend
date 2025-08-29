# push_tokens/urls.py
from django.urls import path
from .views import PushTokenView, PushNotificationView, PushNotificationTestView

urlpatterns = [
    path('push-tokens', PushTokenView.as_view(), name='push-tokens'),
    path('push-notifications', PushNotificationView.as_view(), name='push-notifications'),
    path('push-notifications/test', PushNotificationTestView.as_view(), name='push-notifications-test'),
]
