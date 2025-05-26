from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from .utils import get_daily_stock_prices
import logging
logger = logging.getLogger('stocks')


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
from collections import deque
import time

# 최근 호출 시간들을 담는 전역 큐 (최대 5개만 유지)
api_call_times = deque()
def throttle_api_call():
    now = time.time()

    # 1초 이상 지난 호출은 제거
    while api_call_times and now - api_call_times[0] > 1:
        api_call_times.popleft()

    if len(api_call_times) > 5:
        # ✅ 호출 제한 초과: 대기
        wait_time = 1 - (now - api_call_times[0])
        time.sleep(wait_time)
        throttle_api_call()  # 재귀 호출

    # ✅ 현재 호출 시간 저장
    api_call_times.append(time.time())

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

        # ✅ 캐시 키 생성 및 날짜 설정
        today = datetime.today()
        end_date = today.strftime("%Y%m%d")
        start_date = (today - timedelta(days=5)).strftime("%Y%m%d")
        cache_key = f"stock_change_{stock_code}_{start_date}_{end_date}"

        # ✅ 캐시 확인
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)

        # ✅ 요청 중복 방지 플래그 확인
        request_flag_key = f"{cache_key}_in_progress"
        if cache.get(request_flag_key):
            return Response(
                {
                    "status": "error",
                    "message": "요청이 너무 자주 발생하고 있습니다. 잠시 후 다시 시도해주세요.",
                    "code": 429
                },
                status=429
            )

        try:
            # ✅ 요청 중임 플래그 설정
            cache.set(request_flag_key, True, timeout=1)
            throttle_api_call()

            # ✅ 최근 5일간의 일봉 데이터 가져오기
            daily_prices = get_daily_stock_prices(stock_code, start_date, end_date)

            # ✅ 400 오류: 데이터 부족 시
            if len(daily_prices) < 2:
                return Response(
                    {
                        "status": "error",
                        "message": "주식 데이터가 부족합니다.",
                        "code": 400
                    },
                    status=400
                )

            # ✅ 날짜 순 정렬 (최신 순)
            sorted_prices = sorted(daily_prices, key=lambda x: x["stck_bsop_date"], reverse=True)
            current_price = int(sorted_prices[0]["stck_clpr"])
            prev_price = int(sorted_prices[1]["stck_clpr"])

            price_change = current_price - prev_price
            price_change_percentage = round((price_change / prev_price) * 100, 2) if prev_price > 0 else 0
            change_status = "up" if price_change > 0 else "down" if price_change < 0 else "unchanged"

            response_data = {
                "status": "success",
                "stock_code": stock_code,
                "current_date": sorted_prices[0]["stck_bsop_date"],
                "current_price": current_price,
                "previous_date": sorted_prices[1]["stck_bsop_date"],
                "previous_price": prev_price,
                "price_change": abs(price_change),
                "price_change_percentage": abs(price_change_percentage),
                "change_status": change_status
            }

            # ✅ 캐시 저장 (1초)
            cache.set(cache_key, response_data, timeout=1)
            return Response(response_data, status=200)

        except ValueError as e:
            message = str(e)
            if "거래건수" in message:
                return Response(
                    {"status": "error", "message": message, "code": 429},
                    status=429
                )
            return Response(
                {"status": "error", "message": message, "code": 502},
                status=502
            )

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"서버에서 예기치 못한 오류 발생: {str(e)}",
                    "code": 500
                },
                status=500
            )

