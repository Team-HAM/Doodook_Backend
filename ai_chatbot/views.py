from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import get_ai_response
from rest_framework.permissions import AllowAny
class AIChatbotView(APIView):
    permission_classes= [AllowAny]
    def post(self,request):
        user_input=request.data.get("message","")
        if not user_input:
            return Response({"error": "message는 필수 입니다."},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reply=get_ai_response(user_input)
            return Response({"reply":reply})
        except Exception as e:
            return Response({"error":str(e)},status.HTTP_500_INTERNAL_SERVER_ERROR)