# push_tokens/urls.py
from django.urls import path
from .views import PushTokenView

urlpatterns = [
    path('push-tokens', PushTokenView.as_view(), name='push-tokens'),
]
