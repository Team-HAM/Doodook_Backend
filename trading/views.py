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
    stock_code = request.GET.get('stock_code', '')  # 쿼리 파라미터로 주식 코드 받기 (기본값은 빈 문자열)

    if not stock_code:
        return JsonResponse({"error": "주식 코드가 필요합니다."}, status=400)

    current_price = get_current_stock_price(stock_code)

    if current_price is None:
        return JsonResponse({"error": "주식 가격을 가져올 수 없습니다."}, status=500)

    return JsonResponse({"stock_code": stock_code, "current_price": current_price})

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

    # 주식 가격 가져오기
    current_price = get_current_stock_price(stock_symbol)
    if current_price is None:
        return JsonResponse({"error": "주식 가격을 가져올 수 없습니다."}, status=500)

    # 현재 가격 확인
    if order_type == "buy" and price < current_price:
        return JsonResponse({"error": f"매수 가격은 현재가 ({current_price}원)보다 높거나 같아야 합니다."}, status=400)

    if order_type == "sell" and price > current_price:
        return JsonResponse({"error": f"매도 가격은 현재가 ({current_price}원)보다 낮거나 같아야 합니다."}, status=400)

    # 사용자별 포트폴리오 가져오기 (없으면 생성)
    portfolio, created = StockPortfolio.objects.get_or_create(user=user, stock_code=stock_symbol)

    if order_type == "buy":
        total_cost = quantity * price

        # 잔고 확인
        if user.balance < total_cost:
            return JsonResponse({"error": "잔고가 부족합니다."}, status=400)

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
            return JsonResponse({"error": "보유 수량 부족"}, status=400)

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
        return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

    return JsonResponse({"message": response})



from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import StockPortfolio  # 사용자와 주식 포트폴리오 모델 임포트
from users.models import User
from .serializers import StockPortfolioSerializer  # 포트폴리오 직렬화기
# 사용자 포트폴리오 조회 및 수익률 계산 API
class PortfolioView(APIView):
    """사용자 포트폴리오 조회 API"""
    
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request, user_id):  # request와 user_id를 받는 방식으로 수정
        # 사용자 확인
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 사용자와 관련된 주식 포트폴리오 정보 가져오기
        stock_portfolio = StockPortfolio.objects.filter(user=user)
        
        # 각 주식의 현재 가격을 가져와 수익률 계산
        portfolio_data = []
        for stock in stock_portfolio:
            current_price = get_current_stock_price(stock.stock_code)
            if current_price:
                # 평균 매수가 계산
                if stock.quantity > 0:
                    average_price = stock.price / stock.quantity  # 평균 매수가 계산
                    profit_rate = ((current_price - average_price) / average_price) * 100
                else:
                    profit_rate = None
            else:
                profit_rate = None

            portfolio_data.append({
                "stock_code": stock.stock_code,
                "quantity": stock.quantity,
                "average_price": average_price if stock.quantity > 0 else None,
                "current_price": current_price,
                "profit_rate": profit_rate
            })
        
        return Response({"portfolio": portfolio_data}, status=status.HTTP_200_OK)
