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
# from users.serializers import UserLoginSerializer

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
# from .serializers import UserLoginSerializer  # Replace with the correct path if the serializer is in a different location

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

# 공통 오류 응답 함수
def error_response(message, code):
    return JsonResponse({
        "status": "error",
        "message": message,
        "code": code
    }, status=code)

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

from .models import UserActivation
# views.py
# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User, UserActivation

class ActivateUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            activation = UserActivation.objects.get(token=token)
        except UserActivation.DoesNotExist:
            return Response({
                "status": "error",
                "message": "인증에 실패하였습니다.",
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        user = activation.user
        if not user.is_active:
            user.is_active = True
            user.save()
            activation.delete()  # 인증 완료 시 삭제

        return Response({
            "status": "success",
            "message": "계정이 활성화되었습니다."
        })
    
class ActivateWithCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email:
            return Response({"status": "error", "message": "이메일이 필요합니다."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "존재하지 않는 사용자입니다."}, status=404)

        # ✅ 이미 활성화된 경우, 코드가 없어도 성공 처리
        if user.is_active:
            return Response({"status": "success", "message": "이미 인증된 사용자입니다."}, status=200)

        # 코드가 없을 경우 인증 불가
        if not code:
            return Response({"status": "error", "message": "인증 코드가 필요합니다."}, status=400)

        try:
            activation = UserActivation.objects.get(user=user)
        except UserActivation.DoesNotExist:
            return Response({"status": "error", "message": "인증 정보가 없습니다."}, status=404)

        if activation.code == code:
            user.is_active = True
            user.save()
            activation.delete()
            return Response({"status": "success", "message": "계정이 인증되었습니다."}, status=200)

        return Response({"status": "error", "message": "잘못된 인증 코드입니다."}, status=400)

from django.contrib.auth.hashers import check_password   
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
@api_view(['POST'])
@permission_classes([])
def Login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    # 이메일로 사용자 조회
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": "로그인 실패. 이메일 또는 비밀번호가 잘못되었습니다.",
            "code": 401
        }, status=status.HTTP_401_UNAUTHORIZED)

    # 비밀번호 확인 (authenticate() 대신 직접 체크)
    if not check_password(password, user.password):
        return Response({
            "status": "error",
            "message": "로그인 실패. 이메일 또는 비밀번호가 잘못되었습니다.",
            "code": 401
        }, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # ✅ Simple JWT 방식으로 토큰 생성
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        
        update_last_login(None, user)  # 마지막 로그인 업데이트

        return Response({
            "status": "success",
            "message": "로그인 성공",
            "data": {
                "access": access,
                "refresh": str(refresh),
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            "status": "error",
            "message": "로그인 중 오류가 발생했습니다. 다시 시도해주세요.",
            "code": 500,
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
from .serializers import AccountSerializer  

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # 인증된 사용자만 접근 가능
def get_user_account(request):
    """현재 로그인한 사용자의 닉네임과 잔액 정보를 반환"""
    try:
        # 사용자 인증 여부 확인
        if not request.user.is_authenticated:
            return error_response("인증이 필요합니다.", 401)
        
        # 로그인한 사용자 정보 조회 및 직렬화
        user_data = AccountSerializer(request.user).data

        # 사용자 정보와 잔액 정보를 함께 반환
        return JsonResponse({
            "status": "success",
            "data": user_data
        }, status=200)

    except User.DoesNotExist:
        # 사용자가 존재하지 않을 경우
        return error_response("사용자를 찾을 수 없습니다.", 404)

    except Exception as e:
        # 일반적인 예외 처리 (서버 내부 오류)
        return error_response(str(e), 500)

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
        
#비밀번호 변경
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChangePasswordSerializer

class ChangePasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if not request.data.get("new_password"):
            return error_response("새 비밀번호를 입력하세요.", 400)

        if serializer.is_valid():
            user = request.user
            
            if user.check_password(serializer.validated_data["new_password"]):
                return error_response("이전과 동일한 비밀번호로 변경할 수 없습니다.", 400)
            
            user.set_password(serializer.validated_data['new_password'])  # 비밀번호 변경
            user.save()
            return Response({
                "status": "success",
                "message": "비밀번호가 성공적으로 변경되었습니다."
            }, status=status.HTTP_200_OK)
        
        return error_response("비밀번호 형식이 올바르지 않습니다.", 400)
    
#비밀번호 재설정
import random
from django.utils import timezone
from django.core.mail import EmailMessage
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import PasswordResetCode

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "이메일을 입력하세요."}, status=400)

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return Response({"error": "가입된 이메일이 없습니다."}, status=404)

        code = str(random.randint(100000, 999999))

        # 기존 코드가 있으면 업데이트
        PasswordResetCode.objects.update_or_create(
            user=user,
            defaults={"code": code, "created_at": timezone.now()}
        )

        EmailMessage(
            subject="[두둑] 비밀번호 재설정 인증번호",
            body=f"인증번호는 [{code}]입니다. 10분 안에 입력해주세요.",
            to=[email]
        ).send()

        return Response({"message": "인증번호를 이메일로 보냈습니다."})


# 비밀번호 재설정 확인
class PasswordResetVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")

        if not all([email, code, new_password]):
            return Response({"error": "모든 값을 입력해주세요."}, status=400)

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return Response({"error": "가입된 이메일이 없습니다."}, status=404)

        try:
            reset_obj = PasswordResetCode.objects.get(user=user, code=code)
        except PasswordResetCode.DoesNotExist:
            return Response({"error": "인증번호가 틀리거나 존재하지 않습니다."}, status=400)

        if reset_obj.is_expired():
            reset_obj.delete()
            return Response({"error": "인증번호가 만료되었습니다."}, status=400)

        user.set_password(new_password)
        user.save()
        reset_obj.delete()

        return Response({"message": "비밀번호가 성공적으로 변경되었습니다."})
