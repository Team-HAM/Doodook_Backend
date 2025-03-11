from django.urls import path
from .views import StockSearchAPIView
from .views import StockAutoCompleteAPIView
urlpatterns = [
    path('search/', StockSearchAPIView.as_view(), name='stock-search'),
    path('autocomplete/', StockAutoCompleteAPIView.as_view(), name='stock-autocomplete'),
]
