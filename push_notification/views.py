from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .utils import send_to_firebase_cloud_messaging

class TestPushNotificationView(APIView):
    permission_classes = [AllowAny]  # 테스트니까 인증은 안 걸어둠

    def post(self, request):
        registration_token = request.data.get("token")
        title = request.data.get("title", "테스트 타이틀")
        body = request.data.get("body", "테스트 메시지")

        if not registration_token:
            return Response({"error": "토큰이 필요합니다."}, status=400)

        try:
            response = send_to_firebase_cloud_messaging(registration_token, title, body)
            return Response({"success": True, "message_id": response})
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)
    