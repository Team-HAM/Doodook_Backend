# point/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from .utils import error_response  # 공통 오류 함수 임포트

User = get_user_model()
from decimal import Decimal, InvalidOperation

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increase_balance(request):
    try:
        amount = request.data.get('amount')

        if amount is None:
            return error_response("금액(amount)을 입력해주세요.", 400)

        try:
            amount = Decimal(str(amount))  # 핵심: Decimal로 변환
            if amount <= 0:
                return error_response("금액은 0보다 커야 합니다.", 400)
        except (ValueError, InvalidOperation):
            return error_response("유효한 숫자를 입력해주세요.", 400)

        user = request.user
        user.balance += amount
        user.save()  # Decimal로 맞춰졌으므로 이 시점에서 save가 실패하면 로그로 잡힘

        return Response({
            "status": "success",
            "message": f"{amount}원이 예수금에 추가되었습니다.",
            "new_balance": float(user.balance),
            "code": 200
        }, status=200)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"예수금 증가 중 오류 발생: {e}")
        return error_response("서버 오류가 발생했습니다.", 500)
