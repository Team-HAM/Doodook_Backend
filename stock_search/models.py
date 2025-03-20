from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True)  # 종목 코드
    name = models.CharField(max_length=100)  # 종목명
    market = models.CharField(max_length=50)  # 시장 구분 (KOSPI, KOSDAQ 등)
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"
