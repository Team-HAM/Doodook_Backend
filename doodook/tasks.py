# doodook/tasks.py
from celery import shared_task
from django.core.cache import cache
from datetime import datetime, timedelta
from .redis_queue import dequeue_stock_codes
from .hantu_api import get_daily_stock_prices    # 기존 함수 그대로 활용

@shared_task
def process_api_queue():
    codes = list(dict.fromkeys(dequeue_stock_codes(n=2)))
    if not codes:
        return

    today       = datetime.today()
    end_date    = today.strftime("%Y%m%d")
    start_date  = (today - timedelta(days=5)).strftime("%Y%m%d")

    for stock_code in codes:
        try:
            daily = get_daily_stock_prices(stock_code, start_date, end_date)
            if len(daily) < 2:
                continue

            # 최신순 정렬
            daily.sort(key=lambda x: x["stck_bsop_date"], reverse=True)
            cur   = int(daily[0]["stck_clpr"])
            prev  = int(daily[1]["stck_clpr"])
            diff  = cur - prev
            pct   = round((diff / prev) * 100, 2) if prev else 0
            state = "up" if diff > 0 else "down" if diff < 0 else "unchanged"

            response = {
                "status":  "success",
                "stock_code": stock_code,
                "current_date":  daily[0]["stck_bsop_date"],
                "current_price": cur,
                "previous_date": daily[1]["stck_bsop_date"],
                "previous_price": prev,
                "price_change":   abs(diff),
                "price_change_percentage": abs(pct),
                "change_status":  state,
            }

            cache_key = f"stock_change_{stock_code}_{start_date}_{end_date}"
            cache.set(cache_key, response, timeout=10)
            print(f"[✅] {stock_code} 캐시에 저장 완료")

        except Exception as e:
            print(f"[❌] {stock_code} 처리 실패: {e}")
