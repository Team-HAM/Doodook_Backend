from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from common import hantu_urls, hantu_tr_id, constants
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET
from .models import OAuthToken, AccessToken

import json
import requests
import dateutil.parser as dt
import uuid

_header = {'content-type': 'application/json'}

# OAuth 토큰 조회
def get_oauth_token(request):
    existing_oauth_token = OAuthToken.objects.all()

    # 기존 OAuth 토큰이 없다면 새로 발급
    if len(existing_oauth_token) == 0:
        req_url = f"{hantu_urls.TST_API_URL_BASE}{hantu_urls.OAUTH_TOKEN_ISSUE}"
        header = _header
        body = {'appkey': HANTU_API_APP_KEY,
                'secretkey': HANTU_API_APP_SECRET,
                'grant_type': 'client_credentials'}

        res = requests.post(req_url, headers=header, data=json.dumps(body))
        new_oauth_token = res.json()

        # 새로 발급된 토큰 저장
        OAuthToken(approval_key=new_oauth_token['approval_key']).save()
        return HttpResponse(status=200)

    # 기존 토큰이 있는 경우
    if len(existing_oauth_token) > 1:
        return HttpResponse(status=500)

    # 기존 토큰이 있고, 발급된 토큰과 동일한지 확인
    new_oauth_token = res.json()
    if existing_oauth_token[0].approval_key == new_oauth_token['approval_key']:
        print("same token")
    else:
        existing_oauth_token[0].delete()
        OAuthToken(approval_key=new_oauth_token['approval_key']).save()

    return HttpResponse(status=200)


# Access 토큰 발급
def issue_access_token(request):
    existing_access_token = AccessToken.objects.all()
    if len(existing_access_token) > 1:
        return HttpResponse(status=500)

    req_url = f"{hantu_urls.TST_API_URL_BASE}{hantu_urls.ACCESS_TOKEN_ISSUE}"
    header = _header
    body = {'appkey': HANTU_API_APP_KEY,
            'appsecret': HANTU_API_APP_SECRET,
            'grant_type': 'client_credentials'}
    
    res = requests.post(req_url, headers=header, data=json.dumps(body))

    new_access_token = res.json()
    if len(existing_access_token) > 0:
        print("ACCESS TOKEN EXISTS")
    else:
        print("NO EXISTING ACCESS TOKEN")
    
    if 'access_token' in new_access_token:
        print("new access token issued successfully")
    else:
        print(f"error {new_access_token['error_code']}:{new_access_token['error_description']}")
        return HttpResponse(status=500)

    if len(existing_access_token) > 0 and existing_access_token[0].access_token == new_access_token['access_token']:
        print("same token")
    else:
        if len(existing_access_token) > 0:
            existing_access_token[0].delete()
        
        new_token = AccessToken(access_token=new_access_token['access_token'], 
                    token_type=new_access_token['token_type'],
                    expires_in=new_access_token['expires_in'],
                    expires_at=timezone.make_aware(dt.parse(new_access_token['access_token_token_expired'])))
        new_token.access_token_expired = new_token.is_token_expired()
        new_token.save()
    
    return HttpResponse(status=200)

# Access 토큰 폐기
def destroy_access_token(request):
    exisiting_access_token = AccessToken.objects.all()
    if len(exisiting_access_token) == 0:
        return HttpResponse(status=500)
    elif len(exisiting_access_token) > 1:
        return HttpResponse(status=500)

    req_url = f"{hantu_urls.TST_API_URL_BASE}{hantu_urls.ACCESS_TOKEN_DESTROY}"
    header = _header
    body = {'appkey': HANTU_API_APP_KEY,
            'appsecret': HANTU_API_APP_SECRET,
            'token': exisiting_access_token[0].access_token}
    
    res = requests.post(req_url, headers=header, data=json.dumps(body))

    res_json = res.json()
    code = 500
    if "code" in res_json:
        code = res_json['code']
        if res_json['code'] == '200':
            # 실제 응답을 보면 실패했어도 200으로 응답이 내려와서 별도 처리 필요할듯
            exisiting_access_token[0].delete()
        else:
            print(f"res : {res_json['code']} | {res_json['message']}")
    else:
        print(f"res : {json.dumps(res_json)}")

    return HttpResponse(status=code)

# 현재가 조회
def get_current_stock_price(request):
    # 종목코드를 URL 파라미터로 받기 (디폴트는 삼성전자 005930)
    stock_code = request.GET.get('symbol', '')  # 기본값을 삼성전자(005930)로 설정

    if not stock_code:
        return HttpResponse("Stock symbol is required.", status=400)

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

