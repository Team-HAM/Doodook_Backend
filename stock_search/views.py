from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .models import Stock
from .serializers import StockSerializer

class StockSearchAPIView(ListAPIView):
    serializer_class = StockSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '').strip()

        # ✅ 400 오류: query 값이 없을 때
        if not query:
            return Response(
                {
                    "status": "error",
                    "message": "검색어(query)를 입력해야 합니다.",
                    "code": 400
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.db.models import Q, Case, When, Value, IntegerField

        queryset = Stock.objects.filter(
            Q(name__icontains=query) | Q(symbol__icontains=query)
        ).annotate(
            priority=Case(
                When(symbol__istartswith=query, then=Value(0)),
                When(name__istartswith=query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            )
        ).order_by('priority')


        # ✅ 404 오류: 검색 결과가 없을 때
        if not queryset.exists():
            return Response(
                {
                    "status": "error",
                    "message": "검색 결과가 없습니다.",
                    "code": 404
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

class StockAutoCompleteAPIView(ListAPIView):
    serializer_class = StockSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '').strip()

        # ✅ 400 오류: query 값이 없을 때
        if not query:
            return Response(
                {
                    "status": "error",
                    "message": "자동완성할 검색어(query)를 입력해야 합니다.",
                    "code": 400
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = Stock.objects.filter(Q(name__icontains=query) | Q(symbol__icontains=query))[:10]

        # ✅ 404 오류: 자동완성할 데이터가 없을 때
        if not queryset.exists():
            return Response(
                {
                    "status": "error",
                    "message": "자동완성할 결과가 없습니다.",
                    "code": 404
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
