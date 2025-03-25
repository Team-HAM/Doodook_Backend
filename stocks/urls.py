from django.urls import path
from .views import DailyStockPriceView,StockPriceChangeView

urlpatterns = [
    path("daily_stock_price/", DailyStockPriceView.as_view(), name="daily_stock_price"),
    # path("price_change/", StockPriceChangeView.as_view(), name="price_change"),
]
