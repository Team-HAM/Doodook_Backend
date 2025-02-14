from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from users.models import Account
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

#JSON 오류 메시지 출력
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse

#CRSF 비활성화
from django.views.decorators.csrf import csrf_exempt


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


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import UserLoginSerializer
from .utils import create_jwt_token  # create_jwt_token을 추가로 임포트합니다.
from django.contrib.auth import authenticate

@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    if request.method == 'POST':
        # 사용자가 보낸 데이터로 시리얼라이저 생성
        serializer = UserLoginSerializer(data=request.data)

        # 시리얼라이저 검증
        if serializer.is_valid():
            # 이메일과 비밀번호를 사용하여 사용자 인증
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # 인증을 시도
            user = authenticate(request, username=email, password=password)

            if user is None:
                return Response({
                    "status": "error",
                    "message": "로그인 실패. 이메일 또는 비밀번호가 잘못되었습니다.",
                    "code": 401
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 로그인 성공, JWT 토큰 생성
            token = create_jwt_token(user)

            response = {
                "status": "success",
                "message": "로그인 성공",
                "data": {
                    "token": token  # 생성된 토큰을 응답 데이터로 반환
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        # 유효하지 않은 요청인 경우
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
    try:
        # 정상 동작
        return render(request, 'base.html')
    except Exception as e:
        # 서버 오류 응답
        return JsonResponse(
            {
                "status": "error",
                "message": "페이지를 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.",
                "code": 500
            },
            status=500
        )




@csrf_exempt  # CSRF 보호를 비활성화
def logout_view(request):
    if request.method == 'POST':
        try:
            logout(request)
            
            # 로그아웃 후 인증되지 않은 상태인지 확인
            if not request.user.is_authenticated:
                return JsonResponse({
                    "status": "success",
                    "message": "로그아웃이 성공적으로 처리되었습니다.",
                    "code": 200
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "로그아웃에 실패했습니다. 다시 시도해주세요.",
                    "code": 500
                })
        except Exception as e:
            # 서버 오류 응답
            return JsonResponse(
                {
                    "status": "error",
                    "message": "로그아웃 처리 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.",
                    "code": 500
                },
                status=500
            )
    else:
        # 잘못된 요청 방식 응답
        return JsonResponse(
            {
                "status": "error",
                "message": "요청 방식이 올바르지 않습니다. POST 요청만 허용됩니다.",
                "code": 405
            },
            status=405
        )
    
    
#계좌 정보 가져오기
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer, AccountSerializer
from .models import Account

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_account(request):
    """현재 로그인한 사용자의 닉네임과 계좌 정보를 반환"""
    try:
        # 로그인한 사용자 정보 조회
        user = request.user
        
        # UserSerializer를 사용하여 사용자 정보 직렬화
        user_data = UserSerializer(user).data
        
        # 로그인한 사용자의 계좌 정보 조회
        account = Account.objects.get(user=user)
        
        # AccountSerializer를 사용하여 계좌 정보 직렬화
        account_data = AccountSerializer(account).data
        
        # 사용자 정보와 계좌 정보를 함께 반환
        return Response({
            "user": user_data,
            "account": account_data
        })

    except Account.DoesNotExist:
        # 계좌 정보가 없는 경우 처리
        return Response({"error": "계좌 정보가 없습니다."}, status=404)
    except Exception as e:
        # 다른 예외 처리
        return Response({"error": str(e)}, status=500)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = request.user  # 로그인한 사용자
            user.delete()  # 사용자 삭제
            return Response({
                "status": "success",
                "message": "회원탈퇴가 완료되었습니다."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "회원탈퇴 처리 중 오류가 발생했습니다.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)