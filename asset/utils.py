from trading.models import StockPortfolio  # trading 앱에서 가져오기
from trading.utils import get_current_stock_price
def calculate_evaluation_amount(user):
    total = 0
    holdings = StockPortfolio.objects.filter(user=user)
    for item in holdings:
        price = get_current_stock_price(item.stock_code)  # 현재가 함수 필요
        total += item.quantity * price
    return total

from users.models import UserBalance

def get_user_cash(user):
    try:
        balance = UserBalance.objects.get(user=user)
        return balance.cash
    except UserBalance.DoesNotExist:
        return 0  # 예수금이 없으면 0원 반환