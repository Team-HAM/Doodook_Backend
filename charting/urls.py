from django.urls import path
from .views import DailyChartView,DailyChartDataView

urlpatterns = [
    path("daily/<str:stock_code>/", DailyChartView.as_view(), name="daily_chart"),  # 🚀 일봉 차트 조회 API
    path("data/<str:stock_code>/", DailyChartDataView.as_view(), name="daily_chart_data"),  # ✅ 새로운 JSON API
]
