from django.shortcuts import render
from django.http import JsonResponse
from trade_hantu.models import AccessToken
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET
from .models import StockPortfolio
import requests
import json

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

# 공통 오류 응답 함수
def error_response(message, code):
    return JsonResponse({
        "status": "error",
        "message": message,
        "code": code
    }, status=code)

# 주식 현재가 조회 함수
def get_current_stock_price(stock_code):
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
        "FID_COND_MRKT_DIV_CODE": "J",  # 코스피
        "FID_INPUT_ISCD": stock_code
    }

    try:
        response = requests.get(req_url, headers=headers, params=params)

        # print("✅ API 응답 상태코드:", response.status_code)
        # print("✅ API 응답 내용:", response.text)

        if response.status_code != 200:
            return None

        data = response.json()

        if "output" not in data:
            return None

        stock_price = data["output"].get("stck_prpr")

        if not stock_price:
            return None

        return float(stock_price)

    except requests.exceptions.RequestException as e:
        print("❌ 요청 예외 발생:", str(e))
        return None



# 주식 가격 조회 뷰
def stock_price(request):
    stock_code = request.GET.get('stock_code', '').strip()  # 공백 제거

    if not stock_code:
        return error_response("유효하지 않은 요청 매개변수입니다.", 400)

    current_price = get_current_stock_price(stock_code)

    if current_price is None:
        return error_response("주식 가격을 가져올 수 없습니다.", 500)

    return JsonResponse({
        "status": "success",
        "stock_code": stock_code,
        "current_price": current_price
    })

# 거래 처리 뷰
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trade(request):
    user = request.user  # 현재 로그인한 사용자

    # 요청 데이터 파싱
    stock_symbol = request.data.get("stock_symbol")
    order_type = request.data.get("order_type")
    quantity = request.data.get("quantity")
    price = request.data.get("price")

    if not stock_symbol or not order_type or quantity is None or price is None:
        return error_response("유효하지 않은 요청 매개변수입니다.", 400)

    # 가격 가져오기
    current_price = get_current_stock_price(stock_symbol)
    if current_price is None:
        return error_response("주식 가격을 가져올 수 없습니다.", 500)

    # 종목명은 DB에서 조회
    try:
        from stock_search.models import Stock  # 실제 모델명으로 수정
        stock_info = Stock.objects.get(symbol=stock_symbol)
        stock_name = stock_info.name
    except Stock.DoesNotExist:
        stock_name = stock_symbol

    # 포트폴리오 생성 또는 업데이트
    portfolio, created = StockPortfolio.objects.get_or_create(
        user=user,
        stock_code=stock_symbol,
        defaults={"stock_name": stock_name}
    )

    if not portfolio.stock_name:
        portfolio.stock_name = stock_name
        portfolio.save()


    # 현재 가격 확인
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

        response = f"{stock_symbol} {quantity}주 매수 완료 ({price}원)"

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

        response = f"{stock_symbol} {quantity}주 매도 완료 ({price}원)"



    else:
        return error_response("잘못된 요청입니다.", 400)

    return JsonResponse({
        "status": "success",
        "message": response
    })

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StockTrade,StockPortfolio
from .models import StockPortfolio  # 사용자와 주식 포트폴리오 모델 임포트
# from users.models import User
from .serializers import StockPortfolioSerializer  # 포트폴리오 직렬화기
# 사용자 포트폴리오 조회 및 수익률 계산 API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StockPortfolio
# from .utils import get_current_stock_price  # 이미 쓰고 있는 함수
import time
from stock_search.models import Stock # stock_search의 모델을 가져오기 (종목명 조회)

class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        stock_portfolio = StockPortfolio.objects.filter(user=user)

        if not stock_portfolio.exists():
            return Response({
                "status": "error",
                "message": "포트폴리오가 존재하지 않습니다.",
                "code": 404
            }, status=404)

        portfolio_data = []
        for i, stock in enumerate(stock_portfolio):
            # 요청 수 제한을 피하기 위해 딜레이
            if i > 0:
                time.sleep(0.25)  # 초당 4건 = 안정권

            current_price = get_current_stock_price(stock.stock_code)
            if current_price is None:
                return Response({
                    "status": "error",
                    "message": f"주식 코드 {stock.stock_code}의 현재가를 가져올 수 없습니다.",
                    "code": 500
                }, status=500)

            # 평균 매입가 및 수익률 계산
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
                "stock_name": stock_name,  # 이 줄 추가!
                "quantity": stock.quantity,
                "average_price": round(average_price, 2),
                "current_price": current_price,
                "profit_rate": round(profit_rate, 2)
            })


        return Response({
            "status": "success",
            "portfolio": portfolio_data
        }, status=200)
