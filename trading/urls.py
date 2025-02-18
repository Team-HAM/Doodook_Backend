from django.urls import path
from .views import stock_price, trade

urlpatterns = [
    path("trade/", trade, name="trade"),  # 매수/매도 API
    # path("portfolio/<int:user_id>/", PortfolioView.as_view(), name="portfolio"),  # 포트폴리오 조회 API
    path("stock_price/", stock_price, name='stock_price'),  # 현재가 조회 API
    # path("profit/<int:user_id>/", ProfitView.as_view(), name="profit"),  # 🚀 수익률 계산 API
]
