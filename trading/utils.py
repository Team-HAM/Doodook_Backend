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
    time.sleep(0.5)
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
    
# utils.py
import time
from collections import deque
from threading import Lock

class RateLimiterWithCache:
    def __init__(self, max_per_second=2, max_per_minute=100, cache_ttl=10):
        time.sleep(0.5)
        self.lock = Lock()
        self.per_second = deque()
        self.per_minute = deque()
        self.cache_ttl = cache_ttl
        self.cache = {}  # stock_code -> (timestamp, value)

        self.max_per_second = max_per_second
        self.max_per_minute = max_per_minute

    def get_cached(self, stock_code):
        time.sleep(0.5)
        now = time.time()
        with self.lock:
            cached = self.cache.get(stock_code)
            if cached:
                ts, value = cached
                if now - ts < self.cache_ttl:
                    return value
        return None

    def set_cache(self, stock_code, value):
        time.sleep(0.5)
        with self.lock:
            self.cache[stock_code] = (time.time(), value)

    def allow_request(self):
        time.sleep(0.5)
        now = time.time()
        with self.lock:
            while self.per_second and now - self.per_second[0] > 1:
                self.per_second.popleft()
            while self.per_minute and now - self.per_minute[0] > 60:
                self.per_minute.popleft()

            if len(self.per_second) < self.max_per_second and len(self.per_minute) < self.max_per_minute:
                self.per_second.append(now)
                self.per_minute.append(now)
                return True
            return False
