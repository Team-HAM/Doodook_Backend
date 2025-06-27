# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Watchlist

class AddToWatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stock_code = request.query_params.get("stock_code")
        user = request.user

        if not stock_code or len(stock_code) != 6:
            return Response({
                "status": "error",
                "message": "유효한 stock_code를 입력해주세요."
            }, status=status.HTTP_400_BAD_REQUEST)

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


class RemoveFromWatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        stock_code = request.query_params.get("stock_code")
        user = request.user

        if not stock_code or len(stock_code) != 6:
            return Response({
                "status": "error",
                "message": "유효한 stock_code를 입력해주세요."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = Watchlist.objects.get(user=user, stock_code=stock_code)
            item.delete()
            return Response({
                "status": "success",
                "message": f"{stock_code}가 관심 목록에서 제거되었습니다."
            }, status=status.HTTP_200_OK)
        except Watchlist.DoesNotExist:
            return Response({
                "status": "error",
                "message": "해당 종목은 관심 목록에 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)



from stock_search.models import Stock

class ListWatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        watchlist = Watchlist.objects.filter(user=user).values_list('stock_code', flat=True)

        # 해당 stock_code들에 대해 주식명 함께 가져오기
        stocks = Stock.objects.filter(symbol__in=watchlist).values('symbol', 'name')

        return Response({
            "status": "success",
            "watchlist": list(stocks)
        }, status=status.HTTP_200_OK)
