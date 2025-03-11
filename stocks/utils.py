import requests
from trade_hantu.models import AccessToken
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET
from django.utils import timezone
import json

def get_valid_access_token():
    """✅ Access Token을 확인하고, 없거나 만료되면 자동 갱신"""
    access_token = AccessToken.objects.first()

    if access_token is None or access_token.is_token_expired():
        print("⚠️ Access Token이 없거나 만료됨. 새로운 토큰 발급 중...")
        
        # ✅ 새로운 Access Token 발급 요청
        req_url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"

        headers = {"content-type": "application/json"}
        payload = {
            "grant_type": "client_credentials",
            "appkey": HANTU_API_APP_KEY,
            "appsecret": HANTU_API_APP_SECRET
        }

        response = requests.post(req_url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"❌ Access Token 발급 실패! 상태 코드: {response.status_code}")
            return None

        data = response.json()
        new_token = data.get("access_token")

        if not new_token:
            print("❌ Access Token이 응답에 없음!")
            return None

        # ✅ 기존 Access Token 삭제 후 새로 저장
        AccessToken.objects.all().delete()
        new_token_obj = AccessToken(
            access_token=new_token,
            token_type=data.get("token_type", ""),
            expires_in=data.get("expires_in", 0),
            expires_at=timezone.now() + timezone.timedelta(seconds=data.get("expires_in", 0))
        )
        new_token_obj.access_token_expired = new_token_obj.is_token_expired()
        new_token_obj.save()

        print(f"✅ 새로운 Access Token 저장 완료: {new_token}")
        return new_token

    return access_token.access_token
def get_daily_stock_prices(stock_code, start_date, end_date):
    """✅ 한국투자증권 API에서 주어진 주식 코드의 일봉 데이터를 가져오는 함수"""
    access_token = get_valid_access_token()  # ✅ Access Token 자동 갱신

    if not access_token:
        return None  # ❌ Access Token이 없으면 None 반환

    # API 요청 URL
    req_url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}",
        "appkey": HANTU_API_APP_KEY,
        "appsecret": HANTU_API_APP_SECRET,
        "tr_id": "FHKST03010100"  # ✅ 일봉 데이터 조회용 TR ID
    }

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",  # ✅ KOSPI: J, KOSDAQ: Q
        "FID_INPUT_ISCD": stock_code,  # ✅ 주식 코드
        "FID_INPUT_DATE_1": start_date,  # ✅ 조회 시작일
        "FID_INPUT_DATE_2": end_date,  # ✅ 조회 종료일
        "FID_PERIOD_DIV_CODE": "D",  # ✅ 일봉 데이터 조회
        "FID_ORG_ADJ_PRC": "0"  # ✅ 수정주가 기준 (0: 수정주가, 1: 원주가)
    }

    # ✅ API 요청 정보 출력 (디버깅용)
    print("📢 API 요청 정보")
    print(f"📢 요청 URL: {req_url}")
    print(f"📢 요청 헤더: {json.dumps(headers, indent=4)}")
    print(f"📢 요청 파라미터: {json.dumps(params, indent=4)}")

    try:
        response = requests.get(req_url, headers=headers, params=params)

        print(f"📢 API 응답 상태 코드: {response.status_code}")  # ✅ 상태 코드 출력
        print(f"📢 API 응답 데이터 (Raw): {response.text}")  # ✅ 전체 응답 데이터 출력

        if response.status_code != 200:
            print("❌ API 요청 실패!")
            return None  

        data = response.json()

        # ✅ API 응답 구조 확인 (msg_cd 값 체크)
        if "msg_cd" in data and data["msg_cd"] != "MCA00000":
            print(f"❌ API 요청 오류 코드: {data['msg_cd']}, 메시지: {data['msg1']}")
            return None  

        # ✅ `output2`에서 일봉 데이터 가져오기
        if "output2" not in data or not data["output2"]:
            print("❌ 'output2' 키가 응답 데이터에 없음")
            return None  

        return data["output2"]  # ✅ 정상적인 일봉 데이터 반환
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 예외 발생: {e}")
        return None  
