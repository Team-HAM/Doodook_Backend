from django.db import models
from django.conf import settings

class PointHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)  # 적립한 날짜
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'date')  # 하루에 한 번만 적립 허용
