import requests
from django.conf import settings
from trade_hantu.models import AccessToken   # AccessToken 모델이 있는 앱 경로로 조정

REQ_URL = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
HEADERS_BASE = {
    "content-type": "application/json",
    "appkey": settings.HANTU_API_APP_KEY,
    "appsecret": settings.HANTU_API_APP_SECRET,
    "tr_id": "FHKST01010100",
}

def get_daily_stock_prices(stock_code: str,
                           start_date: str,  # YYYYMMDD
                           end_date: str) -> list[dict]:
    """
    한국투자증권 일봉(주식 OHLCP) 조회 – 성공 시 output 리스트 반환.
    오류 시 ValueError 발생하며 rt_cd·msg1 출력.
    """
    access_row = AccessToken.objects.first()
    if not access_row or not access_row.access_token:
        raise ValueError("access token 없음")

    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-price"

    headers = {
        **HEADERS_BASE,                               # content-type / appkey / appsecret
        "authorization": f"Bearer {access_row.access_token}",
        "tr_id": "FHKST01010400",
        "custtype": "P",                              # ← 중요: 개인 (P) or 법인 (B)
    }

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",                # 코스피( J ) / 코스닥( Q ) 등
        "FID_INPUT_ISCD": stock_code,
        "FID_INPUT_DATE_1": start_date,
        "FID_INPUT_DATE_2": end_date,
        "FID_PERIOD_DIV_CODE": "D",                   # D = 일봉
        "FID_ORG_ADJ_PRC": "0",                       # 0 = 무수정, 1 = 수정주가
    }

    resp = requests.get(url, headers=headers, params=params, timeout=5)
    try:
        data = resp.json()
    except ValueError:
        raise ValueError(f"JSON 파싱 실패 (status {resp.status_code})")

    # ── 한국투자증권 API는 rt_cd · msg1으로 성공/실패를 알려줌 ──
    if data.get("rt_cd") != "0":
        raise ValueError(f"일봉 API 오류 rt_cd={data.get('rt_cd')} / msg={data.get('msg1')}")

    output = data.get("output")
    if not output:
        raise ValueError("일봉 API 응답에 output 없음")

    return output
