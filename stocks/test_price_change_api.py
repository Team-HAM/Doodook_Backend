import requests
import time

BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/stocks/price_change/"
STOCK_CODE = "005930"  # 삼성전자 (변경 가능)

NUM_REQUESTS = 20       # 몇 번 호출할지
INTERVAL = 0.1          # 몇 초 간격으로 요청할지 (0.1초 = 초당 10회)

def test_price_change_api():
    status_counts = {}  # 응답 코드별 카운트 저장용

    for i in range(NUM_REQUESTS):
        try:
            response = requests.get(
                f"{BASE_URL}{ENDPOINT}",
                params={"stock_code": STOCK_CODE}
            )
            status = response.status_code
            json_data = response.json()
            message = json_data.get("message", "")
            print(f"[{i+1}] {status} - {message}")

            # 상태 코드 카운트 기록
            status_counts[status] = status_counts.get(status, 0) + 1

        except Exception as e:
            print(f"[{i+1}] ❌ 요청 실패: {e}")
            status_counts["error"] = status_counts.get("error", 0) + 1

        time.sleep(INTERVAL)

    # ✅ 결과 요약 출력
    print("\n📊 테스트 결과 요약:")
    for code, count in status_counts.items():
        print(f" - {code}: {count}회")

if __name__ == "__main__":
    test_price_change_api()