from django.db import models
from django.conf import settings

class StockPortfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    stock_code = models.CharField(max_length=10)  # 주식 코드
    quantity = models.IntegerField(default=0)     # 보유 수량
    price = models.IntegerField(default=0)        # 주식 가격 (가상 시뮬레이션)
    
    def __str__(self):
        return f"{self.stock_code} - {self.quantity}주"


