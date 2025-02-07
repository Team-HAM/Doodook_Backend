
from django.db import models

class StockPortfolio(models.Model):
    stock_code = models.CharField(max_length=10)  # 주식 코드
    quantity = models.IntegerField(default=0)     # 보유 수량
    price = models.IntegerField(default=0)        # 주식 가격 (가상 시뮬레이션)
    
    def __str__(self):
        return f"{self.stock_code} - {self.quantity}주"


