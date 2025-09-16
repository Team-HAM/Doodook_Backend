

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stock_search.models import Stock
from trading.models import StockPortfolio
from trading.utils import get_current_stock_price
import time
from stock_search.models import Stock
class AssetSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        stock_portfolio = StockPortfolio.objects.filter(user=user)
        total_evaluation = 0
        breakdown = []

        # 캐시 딕셔너리 생성
        price_cache = {}
        name_cache = {}

        for stock in stock_portfolio:
            stock_code = stock.stock_code
            # time.sleep(0.5)  # 모든 API 요청 전에 0.5초 대기

            # 현재가 캐시 확인
            if stock_code in price_cache:
                current_price = price_cache[stock_code]
            else: 
                time.sleep(0.5)
                current_price = get_current_stock_price(stock_code)
                price_cache[stock_code] = current_price
            
            if current_price is None:
                print(f"❗ {stock_code} 현재가 없음, 건너뜀")
                continue

            value = stock.quantity * current_price
            total_evaluation += value

            # ✅ 종목명이 없으면 stock_search DB에서 찾아서 저장
            if not stock.stock_name:
                if stock_code in name_cache:
                    stock_name = name_cache[stock_code]
                else:
                    try:
                        
                        stock_info = Stock.objects.get(symbol=stock.stock_code)
                        stock.stock_name = stock_info.name
                        name_cache[stock_code] = stock_name
                        stock.stock_name = stock_name
                        stock.save()
                        print(f"📌 종목명 저장됨: {stock_info.name}")
                    except Stock.DoesNotExist:
                        stock_name = stock_code
                        print(f"❗ 종목명 DB에 없음: {stock.stock_code}")

            # stock_name = stock.stock_name or stock.stock_code  # fallback
            else:
                stock_name = stock.stock_name
            
            breakdown.append({
                "label": stock_name,
                "value": value
            })

        

        # 예수금 가져오기
        cash = float(request.user.balance)  # Decimal → float

        breakdown.insert(0, {
            "label": "예수금",
            "value": cash
        })

        total_asset = total_evaluation + cash

        return Response({
            "status": "success",
            "cash": cash,
            "evaluation": total_evaluation,
            "total_asset": total_asset,
            "breakdown": breakdown  # 프론트의 원형 그래프용 데이터
        })
