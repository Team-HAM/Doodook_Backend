from django.shortcuts import render
from django.http import JsonResponse
from trade_hantu.models import AccessToken
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET
from .models import StockPortfolio
import requests
import json
import time
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

# 주식 현재가 조회 함수
def get_current_stock_price(stock_code):
    time.sleep(0.3)
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