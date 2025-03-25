from django.urls import path
from .views import MBTIQuestionListView

urlpatterns = [
    path('questions/', MBTIQuestionListView.as_view(), name='mbti-questions-list'),
]