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
        try:
            # 주식 코드 설정
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
            
            # 주식 가격 요청
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식현재가요청", "opt10001", 0, "0101")

            # 이벤트 루프 실행
            self.event_loop = QEventLoop()
            self.kiwoom.OnReceiveTrData.connect(self._on_receive_tr_data)
            
            # 이벤트 루프가 종료될 때까지 대기
            self.event_loop.exec_()

            # 가격 조회 실패 시
            if self.price is None:
                raise ValueError(f"주식 코드 '{stock_code}'에 대한 가격 조회 실패.")
            
            return self.price

        except Exception as e:
            # 예외 발생 시 오류 메시지 출력
            print(f"주식 가격 조회 오류: {e}")
            # 예외를 그대로 던져서 trade 함수에서 처리할 수 있도록 함
            raise Exception(f"주식 가격 조회 중 오류가 발생했습니다: {str(e)}")


    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "주식현재가요청":
            try:
                price_str = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, 0, "현재가").strip()

                # 빈 문자열 체크
                if not price_str:
                    raise ValueError(f"주식 가격 조회 실패: {msg1} - {msg2}")

                # 정수로 변환
                self.price = int(price_str)

            except ValueError as e:
                print(f"주식 가격 조회 오류: {e}")
                self.price = None  # 가격을 None으로 설정하여 이후 처리 가능하도록 함
            except Exception as e:
                print(f"예상치 못한 오류 발생: {e}")
                self.price = None
            finally:
                # 이벤트 루프 종료
                self.event_loop.quit()


def get_stock_price(stock_code):
    try:
        api = KiwoomAPI()
        return api.get_current_price(stock_code)
    except Exception as e:
        print(f"주식 가격 조회 오류: {e}")
        return None


def stock_price(request):  # 최근에 만든
    if request.method == "GET":
        stock_code = request.GET.get("stock_code")  # 주식 코드 입력 받기

        if not stock_code:
            return JsonResponse({
                "status": "error",
                "message": "유효하지 않은 요청 매개변수입니다.",
                "code": 400
            }, status=400)

        try:
            # 주식의 현재 가격을 조회
            current_price = get_stock_price(stock_code)

            if current_price is None:  # 주식 코드가 없거나 데이터를 못 가져왔을 경우
                return JsonResponse({
                    "status": "error",
                    "message": f"'{stock_code}' 주식 가격 조회에 실패했습니다.",
                    "code": 404
                }, status=404)

            # 성공적으로 데이터를 가져온 경우
            return JsonResponse({
                "status": "success",
                "stock_code": stock_code,
                "current_price": current_price
            })
        
        except Exception as e:
            # 기타 예외를 처리
            return JsonResponse({
                "status": "error",
                "message": f"서버에서 예기치 못한 오류가 발생했습니다: {str(e)}",
                "code": 500
            }, status=500)
def trade(request): # 매수/매도
    if request.method == "POST":
        action = request.POST.get("action")
        stock_code = request.POST.get("stock_code")
        try:
            quantity = int(request.POST.get("quantity"))
            price = int(request.POST.get("price"))
        except (TypeError, ValueError):
            return JsonResponse({
                "status": "error",
                "message": "유효하지 않은 요청 매개변수입니다.",
                "code": 400
            }, status=400)

        current_price = get_stock_price(stock_code)

        if current_price is None:
            return JsonResponse({
                "status": "error",
                "message": "주식 가격 조회에 실패했습니다.",
                "code": 500
            }, status=500)

        # 로그: 실제 비교되는 값 확인
        print(f"현재 가격: {current_price}, 매도 가격: {price}")  # 디버깅용 로그

        if action == "buy":
            if price >= current_price:
                portfolio, created = StockPortfolio.objects.get_or_create(stock_code=stock_code)
                portfolio.quantity += quantity
                portfolio.price = price
                portfolio.save()
                response = f"매수 주문이 완료되었습니다: {quantity}주 {stock_code}를 {price}에 매수했습니다."
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"매수 실패: 현재 가격({current_price})보다 높은 가격으로 매수할 수 없습니다.",
                    "code": 400
                }, status=400)

        elif action == "sell":
            # 가격 비교 명확히 하기 위해 int로 변환
            if int(price) < int(current_price):
                # 오류 발생시 처리
                print(f"매도 가격({price})이 현재 가격({current_price})보다 낮습니다.")  # 디버깅용 로그
                return JsonResponse({
                    "status": "error",
                    "message": f"매도 실패: 현재 가격({current_price})보다 낮은 가격으로 매도할 수 없습니다.",
                    "code": 400
                }, status=400)
            else:
                portfolio = StockPortfolio.objects.filter(stock_code=stock_code).first()
                if portfolio:
                    if portfolio.quantity >= quantity:
                        portfolio.quantity -= quantity
                        portfolio.save()
                        response = f"매도 주문이 완료되었습니다: {quantity}주 {stock_code}를 {price}에 매도했습니다."
                    else:
                        return JsonResponse({
                            "status": "error",
                            "message": "매도할 주식이 부족하거나 존재하지 않습니다.",
                            "code": 400
                        }, status=400)
                else:
                    return JsonResponse({
                        "status": "error",
                        "message": f"'{stock_code}'에 대한 주식 포트폴리오가 존재하지 않습니다.",
                        "code": 400
                    }, status=400)

        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid action.",
                "code": 400
            }, status=400)

        return JsonResponse({"message": response})

    # GET 요청 처리
    try:
        portfolios = StockPortfolio.objects.all()
        if not portfolios.exists():
            return JsonResponse({
                "status": "error",
                "message": "거래 내역이 없습니다.",
                "code": 404
            }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": "서버 내부 오류로 거래 내역을 불러올 수 없습니다.",
            "code": 500
        }, status=500)

    return render(request, "users/trade.html", {"portfolios": portfolios})
