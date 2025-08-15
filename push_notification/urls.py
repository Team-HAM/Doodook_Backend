from django.urls import path
from push_notification.views import TestPushNotificationView

urlpatterns = [
    path("push/test/", TestPushNotificationView.as_view(), name="push-test"),
    
]
