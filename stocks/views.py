from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .utils import get_daily_stock_prices
import time

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

            # ✅ 전일 대비 상승/하락 정보 추가 및 프론트에서 쉽게 사용할 수 있도록 데이터 변환
            # API 응답에서 날짜 기준으로 데이터 정렬 (최신 날짜가 먼저 오도록)
            sorted_daily_prices = sorted(daily_prices, key=lambda x: x["stck_bsop_date"], reverse=True)

            # ✅ 프론트에서 쉽게 사용할 수 있도록 데이터 변환
            chart_data = []
            for i, item in enumerate(sorted_daily_prices):
                current_close = int(item["stck_clpr"])

                # 전일 데이터가 있는 경우에만 변동 계산
                if i < len(sorted_daily_prices) - 1:
                    prev_close = int(sorted_daily_prices[i + 1]["stck_clpr"])
                    price_change = current_close - prev_close
                    price_change_percentage = round((price_change / prev_close) * 100, 2) if prev_close > 0 else 0
                    change_status = "up" if price_change > 0 else "down" if price_change < 0 else "unchanged"
                else:
                    price_change = 0
                    price_change_percentage = 0
                    change_status = "unchanged"

                chart_data.append({
                    "date": datetime.strptime(item["stck_bsop_date"], "%Y%m%d").strftime("%Y-%m-%d"),
                    "open": int(item["stck_oprc"]),
                    "high": int(item["stck_hgpr"]),
                    "low": int(item["stck_lwpr"]),
                    "close": current_close,
                    "volume": int(item["acml_vol"]),
                    "price_change": abs(price_change),
                    "price_change_percentage": abs(price_change_percentage),
                    "change_status": change_status
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
            )  # 함수 호출 끝에 필요한 닫는 괄호 추가


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

class StockPriceChangeView(APIView):
    """✅ 주식 가격 전일 대비 변동 정보 조회 API"""

    permission_classes = [AllowAny]  # ✅ 누구나 접근 가능

    def get(self, request):
        stock_code = request.GET.get("stock_code", "")

        # ✅ 400 오류: stock_code가 없거나 잘못된 형식일 때
        if not stock_code or not stock_code.isdigit() or len(stock_code) != 6:
            return Response(
                {
                    "status": "error",
                    "message": "유효하지 않은 주식 코드입니다.",
                    "code": 400
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # ✅ 초당 요청 제한 회피: 요청 간 0.25초 지연
            time.sleep(0.25)

            # ✅ 오늘과 5일 전 날짜 계산 (주말/공휴일 고려하여 5일 전부터 데이터 요청)
            today = datetime.today()
            end_date = today.strftime("%Y%m%d")
            start_date = (today - timedelta(days=5)).strftime("%Y%m%d")  # 최근 5일간의 데이터 요청

            # ✅ 최근 5일간의 일봉 데이터 가져오기
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

            # ✅ 날짜 순으로 정렬 (최신 데이터가 인덱스 0에 오도록)
            sorted_prices = sorted(daily_prices, key=lambda x: x["stck_bsop_date"], reverse=True)

            # ✅ 최근 거래일과 그 전 거래일 데이터 가져오기
            current_price = int(sorted_prices[0]["stck_clpr"])
            prev_price = int(sorted_prices[1]["stck_clpr"])

            price_change = current_price - prev_price
            price_change_percentage = round((price_change / prev_price) * 100, 2) if prev_price > 0 else 0
            change_status = "up" if price_change > 0 else "down" if price_change < 0 else "unchanged"

            return Response(
                {
                    "status": "success",
                    "stock_code": stock_code,
                    "current_date": sorted_prices[0]["stck_bsop_date"],
                    "current_price": current_price,
                    "previous_date": sorted_prices[1]["stck_bsop_date"],
                    "previous_price": prev_price,
                    "price_change": abs(price_change),
                    "price_change_percentage": abs(price_change_percentage),
                    "change_status": change_status
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