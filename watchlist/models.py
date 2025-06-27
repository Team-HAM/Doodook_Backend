from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class AddToWatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, stock_code):
        user = request.user

        if Watchlist.objects.filter(user=user, stock_code=stock_code).exists():
            return Response({
                "status": "error",
                "message": "이미 관심 목록에 등록된 종목입니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        Watchlist.objects.create(user=user, stock_code=stock_code)
        return Response({
            "status": "success",
            "message": f"{stock_code}가 관심 목록에 추가되었습니다."
        }, status=status.HTTP_201_CREATED)
    
from django.conf import settings

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock_code = models.CharField(max_length=6)

    class Meta:
        unique_together = ('user', 'stock_code')
        verbose_name = '관심 주식'
        verbose_name_plural = '관심 주식 목록'

    def __str__(self):
        return f'{self.user.username} - {self.stock_code}'
