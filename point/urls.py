from django.urls import path
from .views import increase_balance

urlpatterns = [
    path('increase_balance/', increase_balance, name='increase-balance'),
]
