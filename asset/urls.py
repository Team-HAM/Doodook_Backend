# asset/urls.py
from django.urls import path
from .views import AssetSummaryView

urlpatterns = [
    path('summary/', AssetSummaryView.as_view(), name='user-asset-summary'),
]
