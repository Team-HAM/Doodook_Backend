import requests
import time

BASE_URL = "http://127.0.0.1:8000"  # 로컬 서버 주소 또는 배포 서버 주소
STOCK_CODE = "005930"

# ✅ 전일 대비 상승 조회 API 테스트
ENDPOINT = "/stocks/price_change/"

# ✅ 테스트 요청: 초당 10회로 제한 초과 여부 확인
for i in range(50):
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", params={"stock_code": STOCK_CODE})
        print(f"[{i+1}] {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"[{i+1}] ❌ 요청 실패:", e)
    time.sleep(0.1)  # 0.1초 간격 = 초당 10회