import requests
import time

# 변경: 로컬 테스트 주소 또는 배포 서버 주소
BASE_URL = "http://127.0.0.1:8000"
STOCK_CODE = "005930"

for i in range(50):
    try:
        response = requests.get(f"{BASE_URL}/trading/stock_price/", params={"stock_code": STOCK_CODE})
        print(f"[{i+1}] {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[{i+1}] ❌ 요청 실패:", e)
    time.sleep(0.1)  # 0.1초 간격 (10회/초)
