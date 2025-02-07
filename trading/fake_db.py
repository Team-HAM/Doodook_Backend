import json
import os

DB_FILE = "trading/fake_db.json"

# 기본값 설정
users = {
    "1": {"username": "Alice", "balance": 1000000, "stocks": {}},
    "2": {"username": "Bob", "balance": 500000, "stocks": {}}
}
orders = []

def save_to_file():
    """ 현재 users와 orders 데이터를 JSON 파일에 저장 """
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users, "orders": orders}, f, indent=4)
    except Exception as e:
        print(f"⚠️ 데이터 저장 실패: {e}")

def load_from_file():
    """ JSON 파일에서 데이터를 불러와 users, orders를 업데이트 """
    global users, orders
    if os.path.exists(DB_FILE):
        try:
            if os.path.getsize(DB_FILE) == 0:
                print("⚠️ JSON 파일이 비어 있음. 기본값으로 초기화합니다.")
                save_to_file()

            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                # ✅ users가 없으면 기본값으로 설정
                users = data.get("users", users)
                if not users:
                    print("⚠️ users 데이터가 없음. 기본값으로 초기화합니다.")
                    users = {
                        "1": {"username": "Alice", "balance": 1000000, "stocks": {}},
                        "2": {"username": "Bob", "balance": 500000, "stocks": {}}
                    }
                    save_to_file()

                # ✅ orders도 확인
                orders = data.get("orders", orders)

        except json.JSONDecodeError:
            print("⚠️ JSON 파일이 손상됨. 기본값으로 초기화합니다.")
            save_to_file()

        except Exception as e:
            print(f"⚠️ 데이터 불러오기 실패: {e}")

# 🚀 **서버 시작 시 JSON 파일에서 데이터 불러오기**
load_from_file()
print("🚀 서버 시작! 현재 users 데이터:", users)
