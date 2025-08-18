# push/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PushToken
from .serializers import PushTokenSerializer

class PushTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = PushTokenSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        obj, created = PushToken.objects.update_or_create(
            token=data["token"],                                  # token 기준 upsert
            defaults={
                "user": request.user,
                "device_id": data.get("deviceId"),
                "platform": data.get("platform", "web"),
            },
        )
        return Response(
            {"ok": True, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request):
        # 필요 시 제거용: token로 삭제
        token = request.data.get("token")
        if not token:
            return Response({"detail": "token is required"}, status=400)
        deleted, _ = PushToken.objects.filter(user=request.user, token=token).delete()
        return Response(status=status.HTTP_204_NO_CONTENT if deleted else status.HTTP_404_NOT_FOUND)
