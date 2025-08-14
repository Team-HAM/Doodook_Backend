from django.shortcuts import render
from django.http import JsonResponse
from trade_hantu.models import AccessToken
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET
from .models import StockPortfolio
import requests
import json
import time

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .utils import RateLimiterWithCache
from stock_search.models import Stock
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import StockTrade,StockPortfolio
from .models import StockPortfolio  # 사용자와 주식 포트폴리오 모델 임포트


rate_limiter = RateLimiterWithCache()

# 공통 오류 응답 함수
def error_response(message, code=400):
    return JsonResponse({
        "status": "error",
        "message": message,
        "code": code
    }, status=code)

# 주식 현재가 + 등락률 조회 함수
def get_current_stock_price(stock_code):
    time.sleep(0.5)
    cached = rate_limiter.get_cached(stock_code)
    if cached is not None:
        return cached

    if not rate_limiter.allow_request():
        print("🚫 요청 제한. 캐시도 없고 API 호출도 불가.")
        return None

    try:
        access_token = AccessToken.objects.first()
        if access_token is None or not access_token.access_token:
            print("❗️Access token 없음")
            return None

        req_url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {access_token.access_token}",
            "appkey": HANTU_API_APP_KEY,
            "appsecret": HANTU_API_APP_SECRET,
            "tr_id": "FHKST01010100"
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }

        response = requests.get(req_url, headers=headers, params=params, timeout=3)

        if response.status_code != 200:
            print(f"❗️API 상태코드 오류: {response.status_code}, 응답: {response.text}")
            return None

        data = response.json()
        output = data.get("output")
        if not isinstance(output, dict):
            print("❗️output 필드가 이상함:", output)
            return None

        stock_price = float(output.get("stck_prpr", 0))
        change_rate = float(output.get("prdy_ctrt", 0))  # 전일 대비 증감률 (%)

        result = {
            "current_price": stock_price,
            "change_rate": change_rate
        }

        rate_limiter.set_cache(stock_code, result)
        return result

    except requests.exceptions.RequestException as e:
        print("❌ 외부 요청 예외:", e)
        return None
    except Exception as e:
        print("❌ 예외 발생:", e)
        return None

# 주식 가격 조회 뷰
def stock_price(request):
    time.sleep(0.5)
    stock_code = request.GET.get('stock_code', '').strip()

    current_data = get_current_stock_price(stock_code)

    if current_data is None:
        return error_response("현재가를 가져올 수 없습니다. 잠시 후 다시 시도해주세요.", 200)

    return JsonResponse({
        "status": "success",
        "stock_code": stock_code,
        "current_price": current_data["current_price"],
        "change_rate": current_data["change_rate"]
    })

# 거래 처리 뷰
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trade(request):
    time.sleep(0.5)
    user = request.user

    stock_symbol = request.data.get("stock_symbol")
    order_type = request.data.get("order_type")
    quantity = request.data.get("quantity")
    price = request.data.get("price")

    if not stock_symbol or not order_type or quantity is None or price is None:
        return error_response("유효하지 않은 요청 매개변수입니다.", 400)

    current_data = get_current_stock_price(stock_symbol)
    if current_data is None:
        return error_response("주식 가격을 가져올 수 없습니다.", 500)

    current_price = current_data["current_price"]

    try:
        stock_info = Stock.objects.get(symbol=stock_symbol)
        stock_name = stock_info.name
    except Stock.DoesNotExist:
        stock_name = stock_symbol

    portfolio, created = StockPortfolio.objects.get_or_create(
        user=user,
        stock_code=stock_symbol,
        defaults={"stock_name": stock_name}
    )

    if not portfolio.stock_name:
        portfolio.stock_name = stock_name
        portfolio.save()

    if order_type == "buy" and price < current_price:
        return error_response(f"매수 가격은 현재가 ({current_price}원)보다 높거나 같아야 합니다.", 400)

    if order_type == "sell" and price > current_price:
        return error_response(f"매도 가격은 현재가 ({current_price}원)보다 낮거나 같아야 합니다.", 400)

    if order_type == "buy":
        total_cost = quantity * price

        if user.balance < total_cost:
            return error_response("잔고가 부족합니다.", 400)

        user.balance -= total_cost
        user.save()

        portfolio.quantity += quantity
        portfolio.total_cost += total_cost
        portfolio.price = price
        portfolio.save()

        StockTrade.objects.create(
            user=user,
            stock_code=stock_symbol,
            quantity=quantity,
            price=price,
            trade_type="buy"
        )

        response_msg = f"{stock_symbol} {quantity}주 매수 완료 ({price}원)"

    elif order_type == "sell":
        if portfolio.quantity < quantity:
            return error_response("보유 수량이 부족합니다.", 400)

        total_earnings = quantity * price
        proportional_cost = int((portfolio.total_cost / portfolio.quantity) * quantity)
        portfolio.total_cost -= proportional_cost
        portfolio.quantity -= quantity

        if portfolio.quantity == 0:
            portfolio.delete()
        else:
            portfolio.save()

        user.balance += total_earnings
        user.save()

        StockTrade.objects.create(
            user=user,
            stock_code=stock_symbol,
            quantity=quantity,
            price=price,
            trade_type="sell"
        )

        response_msg = f"{stock_symbol} {quantity}주 매도 완료 ({price}원)"

    else:
        return error_response("잘못된 요청입니다.", 400)

    return JsonResponse({
        "status": "success",
        "message": response_msg
    })

# 포트폴리오 조회 + 수익률 + 등락률
def fetch_stock_price(stock, price_cache):
    if stock.stock_code in price_cache:
        return stock, price_cache[stock.stock_code]
    data = get_current_stock_price(stock.stock_code)
    price_cache[stock.stock_code] = data
    return stock, data

class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        time.sleep(0.5)
        user = request.user
        stock_portfolio = StockPortfolio.objects.filter(user=user)

        if not stock_portfolio.exists():
            return Response({
                "status": "error",
                "message": "포트폴리오가 존재하지 않습니다.",
                "code": 404
            }, status=404)

        portfolio_data = []
        price_cache = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(fetch_stock_price, stock, price_cache) for stock in stock_portfolio]

            for future in as_completed(futures):
                stock, current_data = future.result()
                if current_data is None:
                    return Response({
                        "status": "error",
                        "message": f"{stock.stock_code} 현재가를 못가져옴",
                        "code": 500
                    }, status=500)

                current_price = current_data["current_price"]
                change_rate = current_data["change_rate"]

                if stock.quantity > 0 and stock.total_cost > 0:
                    average_price = stock.total_cost / stock.quantity
                    profit_rate = ((current_price - average_price) / average_price) * 100
                else:
                    average_price = 0
                    profit_rate = 0

                try:
                    stock_info = Stock.objects.get(symbol=stock.stock_code)
                    stock_name = stock_info.name
                except Stock.DoesNotExist:
                    stock_name = "Unknown"

                portfolio_data.append({
                    "stock_code": stock.stock_code,
                    "stock_name": stock_name,
                    "quantity": stock.quantity,
                    "average_price": round(average_price, 2),
                    "current_price": current_price,
                    "profit_rate": round(profit_rate, 2),
                    "change_rate": round(change_rate, 2),
                    "change_direction": "up" if change_rate > 0 else "down" if change_rate < 0 else "same"
                })

        return Response({
            "status": "success",
            "portfolio": portfolio_data
        }, status=200)