# test_rate_limit.py
import requests
import threading
import time

# ▶ ❶ 테스트할 엔드포인트 --------------------------
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/stocks/price_change/?stock_code={code}"
STOCK_CODE = "005930"          # 필요하면 다른 코드로 변경
FULL_URL = BASE_URL + ENDPOINT.format(code=STOCK_CODE)
# ------------------------------------------------

# ▶ ❷ 요청 수 / 동시성 설정 -----------------------
REQUESTS_TO_SEND = 10          # 한번에 보낼 총 요청 수
# ------------------------------------------------

def send_request(i):
    try:
        res = requests.get(FULL_URL, timeout=3)
        print(f"{i:02d} ▶ {res.status_code}")
    except requests.RequestException as e:
        print(f"{i:02d} ▶ ERROR {e!s}")

if __name__ == "__main__":
    threads = []
    start = time.time()

    # ❸ 10개의 스레드를 거의 동시에 스타트
    for i in range(REQUESTS_TO_SEND):
        t = threading.Thread(target=send_request, args=(i,))
        threads.append(t)
        t.start()

    # ❹ 모든 스레드가 끝날 때까지 대기
    for t in threads:
        t.join()

    print(f"⏱️ 전체 완료: {round(time.time() - start, 2)} 초")
