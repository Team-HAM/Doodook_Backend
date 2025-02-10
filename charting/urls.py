from django.urls import path
from .views import DailyChartView

urlpatterns = [
    path("daily/<str:stock_code>/", DailyChartView.as_view(), name="daily_chart"),  # 🚀 일봉 차트 조회 API
]
