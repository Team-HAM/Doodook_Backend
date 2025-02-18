from django.shortcuts import render
from django.http import JsonResponse
from trade_hantu.models import OAuthToken, AccessToken
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET
from .models import StockPortfolio
import requests
import json

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
def trade(request):
    if request.method == "POST":
        action = request.POST.get("action")
        stock_code = request.POST.get("stock_code")
        quantity = int(request.POST.get("quantity"))
        price = int(request.POST.get("price"))
        
        # 주식 현재가 가져오기
        current_price = get_current_stock_price(stock_code)

        if current_price is None:
            return JsonResponse({"error": "주식 가격을 가져올 수 없습니다."}, status=500)

        # 매수/매도 조건 체크
        if (action == "buy" and price >= current_price) or (action == "sell" and price <= current_price):
            portfolio, created = StockPortfolio.objects.get_or_create(stock_code=stock_code)
            if action == "buy":
                portfolio.quantity += quantity
                portfolio.price = price
                portfolio.save()
                response = f"매수 주문 완료: {quantity}주 {stock_code}를 {price}에 매수."
            elif action == "sell":
                if portfolio and portfolio.quantity >= quantity:
                    portfolio.quantity -= quantity
                    portfolio.save()
                    response = f"매도 주문 완료: {quantity}주 {stock_code}를 {price}에 매도."
                else:
                    response = "매도할 주식이 부족하거나 존재하지 않습니다."
        else:
            response = "현재가 조건을 만족하지 않아 주문이 실행되지 않았습니다."
        
        return JsonResponse({"message": response})
    
    # GET 요청 시 포트폴리오 보여주기
    portfolios = StockPortfolio.objects.all()
    return render(request, "users/trade.html", {"portfolios": portfolios})
