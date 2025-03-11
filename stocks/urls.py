from django.urls import path
from .views import DailyStockPriceView

urlpatterns = [
    path("daily_stock_price/", DailyStockPriceView.as_view(), name="daily_stock_price"),
]
