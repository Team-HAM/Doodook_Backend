from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from common import hantu_urls, hantu_tr_id, constants
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET
from .models import OAuthToken, AccessToken

import json
import requests
import dateutil.parser as dt
import uuid

_header = {'content-type': 'application/json'}

def get_oauth_token(request):
    existing_oauth_tokens = OAuthToken.objects.all()

    # ✅ 1. 토큰이 없다면 새로 발급
    if not existing_oauth_tokens.exists():
        req_url = f"{hantu_urls.TST_API_URL_BASE}{hantu_urls.OAUTH_TOKEN_ISSUE}"
        body = {
            'appkey': HANTU_API_APP_KEY,
            'secretkey': HANTU_API_APP_SECRET,
            'grant_type': 'client_credentials'
        }

        res = requests.post(req_url, headers=_header, data=json.dumps(body))
        new_oauth_token = res.json()

        OAuthToken(approval_key=new_oauth_token['approval_key']).save()
        return JsonResponse({"message": "신규 토큰 발급 완료"}, status=200)

    # ✅ 2. 토큰이 여러 개면 오류
    if existing_oauth_tokens.count() > 1:
        return JsonResponse({"error": "OAuth 토큰이 2개 이상 존재합니다."}, status=500)

    # ✅ 3. 하나 있을 때는 그대로 유지 (또s는 갱신하고 싶으면 따로 처리)
    return JsonResponse({"message": "기존 토큰 유지"}, status=200)


# Access 토큰 발급
# def issue_access_token(request):
#     existing_access_token = AccessToken.objects.all()
#     if len(existing_access_token) > 1:
#         return HttpResponse(status=500)

#     req_url = f"{hantu_urls.TST_API_URL_BASE}{hantu_urls.ACCESS_TOKEN_ISSUE}"
#     header = _header
#     body = {'appkey': HANTU_API_APP_KEY,
#             'appsecret': HANTU_API_APP_SECRET,
#             'grant_type': 'client_credentials'}
    
#     res = requests.post(req_url, headers=header, data=json.dumps(body))

#     new_access_token = res.json()
#     if len(existing_access_token) > 0:
#         print("ACCESS TOKEN EXISTS")
#     else:
#         print("NO EXISTING ACCESS TOKEN")
    
#     if 'access_token' in new_access_token:
#         print("new access token issued successfully")
#     else:
#         print(f"error {new_access_token['error_code']}:{new_access_token['error_description']}")
#         return HttpResponse(status=500)

#     if len(existing_access_token) > 0 and existing_access_token[0].access_token == new_access_token['access_token']:
#         print("same token")
#     else:
#         if len(existing_access_token) > 0:
#             existing_access_token[0].delete()
        
#         new_token = AccessToken(access_token=new_access_token['access_token'], 
#                     token_type=new_access_token['token_type'],
#                     expires_in=new_access_token['expires_in'],
#                     expires_at=timezone.make_aware(dt.parse(new_access_token['access_token_token_expired'])))
#         new_token.access_token_expired = new_token.is_token_expired()
#         new_token.save()
    
#     return HttpResponse(status=200)

def issue_access_token(request):
    existing_access_token = AccessToken.objects.all()
    if len(existing_access_token) > 1:
        return JsonResponse({"error": "Access token이 2개 이상 존재합니다."}, status=500)

    req_url = f"{hantu_urls.TST_API_URL_BASE}{hantu_urls.ACCESS_TOKEN_ISSUE}"
    header = {'Content-Type': 'application/json'}
    body = {
        'appkey': HANTU_API_APP_KEY,
        'appsecret': HANTU_API_APP_SECRET,
        'grant_type': 'client_credentials'
    }

    try:
        res = requests.post(req_url, headers=header, data=json.dumps(body))
        res.raise_for_status()  # status 200이 아니면 에러 발생
        new_access_token = res.json()

        if 'access_token' not in new_access_token:
            return JsonResponse({
                "error": "응답에 access_token 키가 없습니다.",
                "response": new_access_token
            }, status=500)

        if len(existing_access_token) > 0 and existing_access_token[0].access_token == new_access_token['access_token']:
            print("같은 토큰이라 저장 생략")
        else:
            if len(existing_access_token) > 0:
                existing_access_token[0].delete()

            # ⛔ 예외 가능 지점
            try:
                expires_at = timezone.make_aware(dt.parse(new_access_token['access_token_token_expired']))
            except KeyError:
                return JsonResponse({
                    "error": "access_token_token_expired 키가 없습니다.",
                    "response": new_access_token
                }, status=500)

            new_token = AccessToken(
                access_token=new_access_token['access_token'],
                token_type=new_access_token['token_type'],
                expires_in=new_access_token['expires_in'],
                expires_at=expires_at
            )
            new_token.access_token_expired = new_token.is_token_expired()
            new_token.save()

        return JsonResponse({"message": "토큰 저장 성공"}, status=200)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"요청 실패: {str(e)}"}, status=500)

    except ValueError as e:
        return JsonResponse({"error": f"응답 JSON 파싱 실패: {str(e)}", "raw_response": res.text}, status=500)

    except Exception as e:
        return JsonResponse({"error": f"서버 내부 오류: {str(e)}"}, status=500)

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
# def get_current_stock_price(request):
#     # 종목코드를 URL 파라미터로 받기 (디폴트는 삼성전자 005930)
#     stock_code = request.GET.get('symbol', '')  # 기본값을 삼성전자(005930)로 설정

#     if not stock_code:
#         return HttpResponse("Stock symbol is required.", status=400)

#     # Access Token 확인
#     access_token = AccessToken.objects.first()
#     token = OAuthToken.objects.first()


#     if access_token is None or not access_token.access_token:
#         return HttpResponse("Access Token is not available.", status=400)

#     # API URL 설정
#     req_url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"

    
#     headers = {
#         "content-type": "application/json",
#         "authorization": f"Bearer {access_token.access_token}",
#         "appkey": HANTU_API_APP_KEY,
#         "appsecret": HANTU_API_APP_SECRET,  # 실제 API 키와 시크릿 코드 입력
#         "tr_id": "FHKST01010100"  # 주식 현재가 조회 TR ID
#     }
#     params = {
#         "FID_COND_MRKT_DIV_CODE": "J",  # 국내 주식 코드 (KOSPI: J, KOSDAQ: Q)
#         "FID_INPUT_ISCD": stock_code
#     }
    
#     try:
#         # API 요청 보내기
#         response = requests.get(req_url, headers=headers, params=params)

#         # 응답 상태 코드 확인
#         if response.status_code != 200:
#             return HttpResponse(f"Failed to retrieve stock price. Status code: {response.status_code}", status=500)

#         # 응답 데이터 처리
#         data = response.json()

#         # 예상되는 출력 데이터가 있는지 확인
#         if "output" not in data:
#             return HttpResponse("No data found for stock price.", status=404)

#         # 주식 가격 추출
#         stock_price = data["output"].get("stck_prpr")

#         if not stock_price:
#             return HttpResponse("Stock price data is unavailable.", status=404)

#         # 가격 출력
#         return HttpResponse(f"Current price of {stock_code}: {stock_price}")

#     except requests.exceptions.RequestException as e:
#         # API 요청 중 에러 처리
#         return HttpResponse(f"API request failed: {str(e)}", status=500)

