# doodook/redis_queue.py
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)
QUEUE_NAME = 'stock_price_queue'

def enqueue_stock_code(stock_code):
    redis_client.rpush(QUEUE_NAME, stock_code)

def dequeue_stock_codes(n=2):
    codes = []
    for _ in range(n):
        code = redis_client.lpop(QUEUE_NAME)
        if code:
            codes.append(code.decode("utf-8"))
    return codes
