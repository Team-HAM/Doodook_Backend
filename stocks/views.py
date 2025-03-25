from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .utils import get_daily_stock_prices

class DailyStockPriceView(APIView):
    """✅ 주식 일봉 데이터 조회 API"""

    permission_classes = [AllowAny]  # ✅ 누구나 접근 가능

    def get(self, request):
        stock_code = request.GET.get("stock_code", "")

        # ✅ 400 오류: stock_code가 없거나 잘못된 형식일 때
        if not stock_code or not stock_code.isdigit() or len(stock_code) != 6:
            return Response(
                {
                    "status": "error",
                    "message": "유효하지 않은 요청 매개변수입니다.",
                    "code": 400
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ 기본적으로 최근 30일치 데이터를 가져오도록 설정
        end_date = datetime.today().strftime("%Y%m%d")
        start_date = (datetime.today() - timedelta(days=30)).strftime("%Y%m%d")

        # ✅ 사용자가 직접 start_date, end_date를 지정할 경우
        if request.GET.get("start_date"):
            start_date = request.GET.get("start_date")
        if request.GET.get("end_date"):
            end_date = request.GET.get("end_date")

        # ✅ 400 오류: 날짜 형식이 잘못되었을 경우
        try:
            datetime.strptime(start_date, "%Y%m%d")
            datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            return Response(
                {
                    "status": "error",
                    "message": "날짜 형식이 올바르지 않습니다. (YYYYMMDD)",
                    "code": 400
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # ✅ 주식 일봉 데이터 가져오기
            daily_prices = get_daily_stock_prices(stock_code, start_date, end_date)

            # ✅ 404 오류: 해당 종목의 데이터가 없을 경우
            if daily_prices is None or len(daily_prices) == 0:
                return Response(
                    {
                        "status": "error",
                        "message": f"'{stock_code}' 주식 가격 조회에 실패했습니다.",
                        "code": 404
                    }, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # ✅ 프론트에서 쉽게 사용할 수 있도록 데이터 변환
            chart_data = []
            for item in daily_prices:
                chart_data.append({
                    "date": datetime.strptime(item["stck_bsop_date"], "%Y%m%d").strftime("%Y-%m-%d"),
                    "open": int(item["stck_oprc"]),
                    "high": int(item["stck_hgpr"]),
                    "low": int(item["stck_lwpr"]),
                    "close": int(item["stck_clpr"]),
                    "volume": int(item["acml_vol"])
                })

            return Response(
                {
                    "status": "success",
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "end_date": end_date,
                    "chart_data": chart_data
                }, 
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # ✅ 500 오류: 서버 예외 처리
            return Response(
                {
                    "status": "error",
                    "message": f"서버에서 예기치 못한 오류가 발생했습니다: {str(e)}",
                    "code": 500
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )