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
    
    
# Create your views here.
class SignupView(CreateAPIView):
    model = get_user_model()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response({"message": "Request Body Error"}, status=status.HTTP_409_CONFLICT)
        if serializer.validated_data['email'] == "None":
            return Response({"message": 'fail'}, status=status.HTTP_200_OK)
        response = {
            'success': True,
            'token': serializer.data['token']
        }
        return Response(response, status=status.HTTP_200_OK)
    
# User Activation View
class UserActivateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uid, token):
        try:
            # UID 디코딩
            real_uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=real_uid)

            # JWT 토큰 디코딩 및 검증
            user_id = jwt_payload_get_user_id_handler(token)
            if user_id is None or int(real_uid) != int(user_id):
                return Response('인증에 실패하였습니다.', status=status.HTTP_400_BAD_REQUEST)

            # 계정 활성화
            user.is_active = True
            user.save()
            return Response(f'{user.email} 계정이 활성화되었습니다.', status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response('유효하지 않은 사용자입니다.', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            return Response('알 수 없는 오류가 발생했습니다.', status=status.HTTP_400_BAD_REQUEST)
