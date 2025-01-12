from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from rest_framework.permissions import AllowAny

#after login
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserLoginSerializer

from rest_framework.views import APIView
import traceback
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from jwt import decode as jwt_decode
from django.conf import settings

#내 프로필 정보 확인&수정하기
from rest_framework.decorators import api_view, permission_classes  # For @api_view and @permission_classes
from rest_framework.response import Response  # For Response
from rest_framework import status  # For status codes like status.HTTP_200_OK
from .serializers import UserLoginSerializer  # Replace with the correct path if the serializer is in a different location

from rest_framework.permissions import IsAdminUser

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

#로그아웃
from django.shortcuts import render, redirect
from django.contrib.auth import logout


User = get_user_model()

# JWT 디코더 함수
def jwt_payload_get_user_id_handler(token):
    try:
        # JWT 토큰 디코딩
        payload = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get('user_id')
    except Exception as e:
        print(f"JWT Decode Error: {e}")
        return None
    
    
class SignupView(CreateAPIView):
    model = get_user_model()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            try:
                # 이메일 전송 로직
                response_data = {
                    "status": "success",
                    "message": "회원가입 성공. 이메일 인증을 진행해주세요.",
                    "data": UserSerializer(user).data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception:
                user.delete()
                return Response({
                    "status": "error",
                    "message": "이메일 전송 실패로 회원가입을 완료할 수 없습니다.",
                    "code": 400
                }, status=status.HTTP_400_BAD_REQUEST)  # 수정: 500 → 400
        return Response({
            "status": "error",
            "message": "유효하지 않은 요청입니다.",
            "code": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            if serializer.validated_data['email'] == "None":
                return Response({
                    "status": "error",
                    "message": "로그인 실패. 이메일 또는 비밀번호가 잘못되었습니다.",
                    "code": 401
                }, status=status.HTTP_401_UNAUTHORIZED)
            response = {
                "status": "success",
                "message": "로그인 성공",
                "data": {
                    "token": serializer.data['token']
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "유효하지 않은 요청입니다.",
            "code": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    
# User Activation View
class UserActivateView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능
    def get(self, request, id):
        token = request.query_params.get('token')
        try:
            user = User.objects.get(pk=id)
            user_id = jwt_payload_get_user_id_handler(token)

            if user_id is None or int(id) != int(user_id):
                return Response({
                    "status": "error",
                    "message": "인증에 실패하였습니다.",
                    "code": 400
                }, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()
            return Response({
                "status": "success",
                "message": "계정이 활성화되었습니다."
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "사용자를 찾을 수 없습니다.",
                "code": 404
            }, status=status.HTTP_404_NOT_FOUND)  # 수정: 400 → 404



#블로그 3편의 내용
@api_view(["GET"])
@permission_classes([IsAdminUser])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def home(request):
    return render(request, 'base.html')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/sessions')  # 수정된 URL로 리디렉션
