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
    # Access Token 확인
    access_token = AccessToken.objects.first()

    if access_token is None or not access_token.access_token:
        return None  # Access token이 없으면 None 반환

    # API URL 설정
    req_url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
    
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {access_token.access_token}",
        "appkey": HANTU_API_APP_KEY,
        "appsecret": HANTU_API_APP_SECRET,
        "tr_id": "FHKST01010100"  # 주식 현재가 조회 TR ID
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",  # 국내 주식 코드 (KOSPI: J, KOSDAQ: Q)
        "FID_INPUT_ISCD": stock_code
    }

    try:
        # API 요청 보내기
        response = requests.get(req_url, headers=headers, params=params)

        # 응답 상태 코드 확인
        if response.status_code != 200:
            return None  # 요청 실패시 None 반환

        # 응답 데이터 처리
        data = response.json()

        if "output" not in data:
            return None  # 데이터가 없다면 None 반환

        # 주식 가격 추출
        stock_price = data["output"].get("stck_prpr")

        if not stock_price:
            return None  # 주식 가격 데이터가 없다면 None 반환

        return float(stock_price)  # 가격을 float로 반환
    except requests.exceptions.RequestException:
        return None  # API 요청 실패시 None 반환


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

    # 주식 가격 가져오기
    current_price = get_current_stock_price(stock_symbol)
    if current_price is None:
        return error_response("주식 가격을 가져올 수 없습니다.", 500)

    # 현재 가격 확인
    if order_type == "buy" and price < current_price:
        return error_response(f"매수 가격은 현재가 ({current_price}원)보다 높거나 같아야 합니다.", 400)

    if order_type == "sell" and price > current_price:
        return error_response(f"매도 가격은 현재가 ({current_price}원)보다 낮거나 같아야 합니다.", 400)

    # 사용자별 포트폴리오 가져오기 (없으면 생성)
    portfolio, created = StockPortfolio.objects.get_or_create(user=user, stock_code=stock_symbol)

    if order_type == "buy":
        total_cost = quantity * price

        # 잔고 확인
        if user.balance < total_cost:
            return error_response("잔고가 부족합니다.", 400)

        # 잔고 차감 및 포트폴리오 갱신
        user.balance -= total_cost
        user.save()

        portfolio.quantity += quantity
        portfolio.price = price  # 마지막 거래 가격 업데이트
        portfolio.save()

        response = f"{stock_symbol} {quantity}주 매수 완료 ({price}원)"
    
    elif order_type == "sell":
        # 보유 주식 수량 확인
        if portfolio.quantity < quantity:
            return error_response("보유 수량이 부족합니다.", 400)

        total_earnings = quantity * price

        # 포트폴리오 업데이트
        portfolio.quantity -= quantity

        # 수량이 0이면 포트폴리오 삭제
        if portfolio.quantity == 0:
            portfolio.delete()
        else:
            portfolio.save()

        # 잔고 업데이트
        user.balance += total_earnings
        user.save()

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
from users.models import User
from .serializers import StockPortfolioSerializer  # 포트폴리오 직렬화기
# 사용자 포트폴리오 조회 및 수익률 계산 API
class PortfolioView(APIView):
    """현재 로그인한 사용자의 포트폴리오 조회 API"""
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # 현재 로그인한 사용자 가져오기
        
        # 사용자의 포트폴리오 조회
        stock_portfolio = StockPortfolio.objects.filter(user=user)
        
        if not stock_portfolio.exists():
            return error_response("포트폴리오가 존재하지 않습니다.", 404)
        
        # 수익률 계산
        portfolio_data = []
        for stock in stock_portfolio:
            current_price = get_current_stock_price(stock.stock_code)
            if current_price is None:
                return error_response(f"주식 코드 {stock.stock_code}의 현재가를 가져올 수 없습니다.", 500)

            # 평균 매수가 계산
            if stock.quantity > 0:
                average_price = stock.price / stock.quantity
                profit_rate = ((current_price - average_price) / average_price) * 100
            else:
                return error_response("보유 수량이 0입니다.", 400)

            portfolio_data.append({
                "stock_code": stock.stock_code,
                "quantity": stock.quantity,
                "average_price": average_price,
                "current_price": current_price,
                "profit_rate": profit_rate
            })
        
        return Response({
            "status": "success",
            "portfolio": portfolio_data
        }, status=status.HTTP_200_OK)
