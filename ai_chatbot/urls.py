from django.urls import path
from .views import AIChatbotView

urlpatterns =[
    path("chat/",AIChatbotView.as_view(),name="ai-chat"),
]