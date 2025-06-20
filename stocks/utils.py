import requests
import json
import hashlib
from django.core.cache import cache
from django.utils import timezone
from trade_hantu.models import AccessToken
from myapi.settings import HANTU_API_APP_KEY, HANTU_API_APP_SECRET

def get_valid_access_token():
    """✅ Access Token을 확인하고, 없거나 만료되면 자동 갱신"""
    access_token = AccessToken.objects.first()

    if access_token is None or access_token.is_token_expired():
        print("⚠️ Access Token이 없거나 만료됨. 새로운 토큰 발급 중...")

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


def get_daily_stock_prices(stock_code, start_date, end_date, cache_ttl=10):
    """
    ✅ 주어진 주식 코드의 일봉 데이터를 캐싱 기반으로 조회
    - 같은 종목+날짜 범위는 API 호출 없이 캐시에서 꺼내 씀
    - 호출 결과는 `cache_ttl`초 동안 캐시됨
    """
    # ✅ 캐시 키 생성 (종목 코드 + 날짜 범위 → 해시로 변환)
    raw_key = json.dumps({
        "code": stock_code,
        "start": start_date,
        "end": end_date
    }, sort_keys=True)
    cache_key = f"daily_prices_{hashlib.sha256(raw_key.encode()).hexdigest()}"

    # ✅ 캐시 확인
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        print("📦 캐시된 일봉 데이터를 반환합니다.")
        return cached_data

    # ✅ 캐시에 없으면 실제 API 호출
    access_token = get_valid_access_token()
    if not access_token:
        return None

    req_url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {access_token}",
        "appkey": HANTU_API_APP_KEY,
        "appsecret": HANTU_API_APP_SECRET,
        "tr_id": "FHKST03010100"
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
        "FID_INPUT_DATE_1": start_date,
        "FID_INPUT_DATE_2": end_date,
        "FID_PERIOD_DIV_CODE": "D",
        "FID_ORG_ADJ_PRC": "0"
    }

    try:
        print("📢 API 요청 시작")
        print(f"📢 요청 파라미터: {json.dumps(params, indent=4)}")

        response = requests.get(req_url, headers=headers, params=params)
        print(f"📢 응답 상태 코드: {response.status_code}")
        print(f"📢 응답 본문: {response.text}")

        data = response.json()

        if response.status_code != 200:
            raise ValueError(f"API 요청 실패: 상태 코드 {response.status_code}")

        if "msg_cd" in data and data["msg_cd"] != "MCA00000":
            print(f"❌ API 응답 에러: {data['msg_cd']} / {data['msg1']}")
            return None

        if "output2" not in data or not data["output2"]:
            print("❌ 'output2' 데이터가 없음")
            return None

        output = data["output2"]

        # ✅ 캐시에 저장
        cache.set(cache_key, output, timeout=cache_ttl)
        print(f"✅ 일봉 데이터 캐시에 저장 완료 ({cache_ttl}초 유효)")

        return output

    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 예외 발생: {e}")
        return None
