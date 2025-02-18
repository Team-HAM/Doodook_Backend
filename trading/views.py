from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from common import hantu_urls, hantu_tr_id, constants
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET
from trade_hantu.models import OAuthToken, AccessToken

import json
import requests
import dateutil.parser as dt
import uuid

def get_current_stock_price(request):
    # 종목코드를 URL 파라미터로 받기 (디폴트는 삼성전자 005930)
    stock_code = request.GET.get('stock_code', '')  # 기본값을 삼성전자(005930)로 설정

    if not stock_code:
        return HttpResponse("Stock code is required.", status=400)

    # Access Token 확인
    access_token = AccessToken.objects.first()
    token = OAuthToken.objects.first()


    if access_token is None or not access_token.access_token:
        return HttpResponse("Access Token is not available.", status=400)

    # API URL 설정
    req_url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"

    
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {access_token.access_token}",
        "appkey": HANTU_API_APP_KEY,
        "appsecret": HANTU_API_APP_SECRET,  # 실제 API 키와 시크릿 코드 입력
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
            return HttpResponse(f"Failed to retrieve stock price. Status code: {response.status_code}", status=500)

        # 응답 데이터 처리
        data = response.json()

        # 예상되는 출력 데이터가 있는지 확인
        if "output" not in data:
            return HttpResponse("No data found for stock price.", status=404)

        # 주식 가격 추출
        stock_price = data["output"].get("stck_prpr")

        if not stock_price:
            return HttpResponse("Stock price data is unavailable.", status=404)

        # 가격 출력
        return HttpResponse(f"Current price of {stock_code}: {stock_price}")

    except requests.exceptions.RequestException as e:
        # API 요청 중 에러 처리
        return HttpResponse(f"API request failed: {str(e)}", status=500)

