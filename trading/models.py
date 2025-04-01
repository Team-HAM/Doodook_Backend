from django.db import models
from django.conf import settings

class StockPortfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    stock_code = models.CharField(max_length=10)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0)  # 마지막 거래 가격
    total_cost = models.IntegerField(default=0)  # 누적 매입 금액 추가

    def __str__(self):
        return f"{self.stock_code} - {self.quantity}주"

class StockTrade(models.Model):
    TRADE_TYPE_CHOICES = [
        ('buy', '매수'),
        ('sell', '매도'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock_code = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    trade_date = models.DateTimeField(auto_now_add=True)
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES, default='buy')

    def __str__(self):
        return f"{self.stock_code} - {self.trade_type} - {self.quantity}주 @ {self.price}"
