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
    
    
# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import StockPortfolio
import sys
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop

# 가상 계좌에 대한 설정
FAKE_ACCOUNT = "123-456-789"  # 하드 코딩된 계좌 번호

class KiwoomAPI:
    def __init__(self):
        self.app = QApplication(sys.argv)  # QApplication 초기화
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.event_loop = QEventLoop()
        self.kiwoom.OnEventConnect.connect(self._on_login)
        self.kiwoom.dynamicCall("CommConnect()")  # 로그인 요청
        self.event_loop.exec_()

    def _on_login(self, err_code):
        if err_code == 0:
            print("Kiwoom API 로그인 성공")
        else:
            print(f"Kiwoom API 로그인 실패, 에러 코드: {err_code}")
        self.event_loop.quit()

    def get_current_price(self, stock_code):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식현재가요청", "opt10001", 0, "0101")
        self.event_loop = QEventLoop()
        self.kiwoom.OnReceiveTrData.connect(self._on_receive_tr_data)
        self.event_loop.exec_()
        return self.price

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "주식현재가요청":
            self.price = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, 0, "현재가").strip())
            self.event_loop.quit()

def get_stock_price(stock_code):
    try:
        api = KiwoomAPI()
        return api.get_current_price(stock_code)
    except Exception as e:
        print(f"주식 가격 조회 오류: {e}")
        return None
    
def stock_price(request): #최근에 만든
    if request.method == "GET":
        stock_code = request.GET.get("stock_code")  # 주식 코드 입력 받기
        
        # 주식의 현재 가격을 조회
        current_price = get_stock_price(stock_code)

        if current_price is None:
            return JsonResponse({"message": "주식 가격 조회에 실패했습니다."})
        
        return JsonResponse({"stock_code": stock_code, "current_price": current_price})

def trade(request):
    if request.method == "POST":
        action = request.POST.get("action")  # 매수 또는 매도
        stock_code = request.POST.get("stock_code")
        quantity = int(request.POST.get("quantity"))
        price = int(request.POST.get("price"))
        
        # 주식의 현재 가격을 조회
        current_price = get_stock_price(stock_code)

        if current_price is None:
            return JsonResponse({"message": "주식 가격 조회에 실패했습니다."})
        
        # 매수/매도 처리
        if action == "buy":
            if price >= current_price:  # 매수 조건: 입력된 가격이 현재 가격 이상
                portfolio, created = StockPortfolio.objects.get_or_create(stock_code=stock_code)
                portfolio.quantity += quantity  # 기존 보유량에 추가
                portfolio.price = price        # 최신 가격 업데이트
                portfolio.save()
                response = f"매수 주문이 완료되었습니다: {quantity}주 {stock_code}를 {price}에 매수했습니다."
            else:
                response = f"매수 실패: 현재 가격({current_price})보다 높은 가격으로 매수할 수 없습니다."

        elif action == "sell":
            if price <= current_price:  # 매도 조건: 입력된 가격이 현재 가격 이하
                portfolio = StockPortfolio.objects.filter(stock_code=stock_code).first()
                if portfolio and portfolio.quantity >= quantity:
                    portfolio.quantity -= quantity  # 수량 차감
                    portfolio.save()
                    response = f"매도 주문이 완료되었습니다: {quantity}주 {stock_code}를 {price}에 매도했습니다."
                else:
                    response = "매도할 주식이 부족하거나 존재하지 않습니다."
            else:
                response = f"매도 실패: 현재 가격({current_price})보다 낮은 가격으로 매도할 수 없습니다."
        
        else:
            response = "Invalid action."

        return JsonResponse({"message": response})
    
    # GET 요청 시 거래 내역을 불러옵니다.
    portfolios = StockPortfolio.objects.all()
    return render(request, "users/trade.html", {"portfolios": portfolios})
