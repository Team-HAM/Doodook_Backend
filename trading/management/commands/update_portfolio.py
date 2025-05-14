from django.core.management.base import BaseCommand
from trading.models import StockPortfolio, StockTrade
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "기존 포트폴리오에 평균 단가(total_cost) 갱신"

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            codes = StockTrade.objects.filter(user=user).values_list('stock_code', flat=True).distinct()
            for code in codes:
                trades = StockTrade.objects.filter(user=user, stock_code=code, trade_type='buy')

                total_quantity = sum(t.quantity for t in trades)
                total_cost = sum(t.quantity * float(t.price) for t in trades)

                if total_quantity == 0:
                    continue

                portfolio, created = StockPortfolio.objects.get_or_create(user=user, stock_code=code)
                portfolio.quantity = total_quantity
                portfolio.total_cost = total_cost
                portfolio.price = trades.latest('trade_date').price
                portfolio.save()

        self.stdout.write(self.style.SUCCESS("✅ 포트폴리오 평균 단가 재계산 완료"))
