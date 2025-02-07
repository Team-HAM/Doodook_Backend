import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TradeSerializer
from .fake_db import users, orders
from .utils import get_stock_price

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import get_stock_price  # Kiwoom API 함수 가져오기

class StockPriceView(APIView):
    """ 특정 종목의 현재가 조회 API """

    permission_classes = [AllowAny]  # ✅ 인증 없이 누구나 접근 가능

    def get(self, request, stock_code):
        price = get_stock_price(stock_code)
        if price is None:
            return Response({"error": "주식 가격 조회 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"stock_code": stock_code, "current_price": price}, status=status.HTTP_200_OK)


logger = logging.getLogger(__name__)  # ✅ 로그 추가

from .fake_db import users, orders, save_to_file

class TradeView(APIView):
    """ 매수 및 매도 API """

    permission_classes = [AllowAny]  # 🚀 인증 없이 접근 가능

    def post(self, request):
        print(f"🚀 매도/매수 요청 데이터: {request.data}")  # ✅ 요청 데이터 로그 추가
        serializer = TradeSerializer(data=request.data)

        if not serializer.is_valid():
            print(f"🚨 TradeSerializer 검증 실패: {serializer.errors}")  # ✅ 오류 로그 추가
            return Response({"error": "잘못된 요청", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data["user_id"]
        stock_code = serializer.validated_data["stock_code"]
        action = serializer.validated_data["action"]
        price = serializer.validated_data["price"]
        quantity = serializer.validated_data["quantity"]

        print(f"✅ TradeSerializer 검증 통과! user_id: {user_id}, action: {action}")  # ✅ 확인 로그

        # 🚀 현재 주가 조회 추가
        current_price = get_stock_price(stock_code)
        print(f"🚀 현재 주가 조회 결과: {current_price}")  # ✅ 주가 조회 로그 추가
        if current_price is None:
            return Response({"error": "주식 가격 조회 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 🚀 users의 키가 문자열일 경우 str(user_id)로 변환
        user_key = str(user_id)

        # 사용자 정보 확인
        if user_key not in users:
            print(f"🚨 사용자 {user_id} 없음! 현재 users: {users}")  # ✅ 디버깅 로그 추가
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user = users[user_key]

        print(f"✅ 사용자 확인 완료! 현재 잔고: {user['balance']}")  # ✅ 사용자 정보 확인 로그 추가

        ### ✅ 매도 로직 ###
        if action == "sell":
            print(f"🚀 매도 시도: {quantity}주, 가격: {price}")  # ✅ 매도 시도 로그 추가

            if stock_code not in user["stocks"]:
                print(f"🚨 매도 실패! 사용자가 {stock_code} 주식을 보유하고 있지 않음")  # ✅ 주식 보유 확인
                return Response({"error": "매도 실패 (보유 주식 없음)"}, status=status.HTTP_400_BAD_REQUEST)

            if user["stocks"][stock_code]["quantity"] < quantity:
                print(f"🚨 매도 실패! 보유 수량: {user['stocks'][stock_code]['quantity']}, 매도 수량: {quantity}")  # ✅ 보유량 체크
                return Response({"error": "매도 실패 (보유 주식 부족)"}, status=status.HTTP_400_BAD_REQUEST)

            user["stocks"][stock_code]["quantity"] -= quantity
            user["balance"] += price * quantity  # 🚀 매도 후 잔고 증가
            print(f"✅ 매도 성공! 남은 보유량: {user['stocks'][stock_code]['quantity']}, 잔고: {user['balance']}")  # ✅ 매도 성공 로그 추가

            if user["stocks"][stock_code]["quantity"] == 0:
                del user["stocks"][stock_code]  # 주식이 0개가 되면 삭제

            # 거래 내역 저장
            orders.append({"user_id": user_id, "stock_code": stock_code, "price": price, "quantity": quantity, "type": "sell"})

            save_to_file()  # 🚀 데이터 저장

            return Response({"message": "매도 완료!", "updated_balance": user["balance"]}, status=status.HTTP_201_CREATED)

        return Response({"error": "잘못된 요청"}, status=status.HTTP_400_BAD_REQUEST)

class PortfolioView(APIView):
    """ 포트폴리오 조회 API """
    
    permission_classes = [AllowAny]  # 🚀 인증 없이 접근 가능하도록 변경

    def get(self, request, user_id):
        user_key = str(user_id)  # 🚀 문자열로 변환

        # 사용자 확인
        if user_key not in users:
            print(f"🚨 사용자 {user_id} 없음! 현재 users: {users}")  # 디버깅 로그 추가
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user = users[user_key]

        # 포트폴리오 데이터 생성
        portfolio = {stock_code: info for stock_code, info in user["stocks"].items()}
        return Response({"portfolio": portfolio}, status=status.HTTP_200_OK)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .fake_db import users
from .utils import get_stock_price

class ProfitView(APIView):
    """ 수익률 계산 API """

    permission_classes = [AllowAny]  # 🚀 인증 없이 접근 가능

    def get(self, request, user_id):
        user_key = str(user_id)  # 🚀 문자열 변환 (users 키가 문자열일 경우 대비)

        # 사용자 확인
        if user_key not in users:
            print(f"🚨 사용자 {user_id} 없음! 현재 users: {users}")  # ✅ 디버깅 로그 추가
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user = users[user_key]

        # 사용자가 보유한 주식 목록 확인
        if "stocks" not in user or not user["stocks"]:
            return Response({"error": "보유 주식이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        portfolio = user["stocks"]
        profit_data = {}

        # 🚀 각 종목별 수익률 계산
        for stock_code, stock_info in portfolio.items():
            avg_price = stock_info["average_price"]  # 평균 매입가
            quantity = stock_info["quantity"]  # 보유 수량
            current_price = get_stock_price(stock_code)  # 현재가 조회

            if current_price is None:
                profit_data[stock_code] = {
                    "error": "현재가 조회 실패"
                }
                continue

            # 🚀 총 매입 금액 vs 현재 평가 금액
            total_purchase_price = avg_price * quantity
            total_current_value = current_price * quantity
            profit_loss = total_current_value - total_purchase_price
            profit_percentage = (profit_loss / total_purchase_price) * 100 if total_purchase_price > 0 else 0

            profit_data[stock_code] = {
                "quantity": quantity,
                "average_price": avg_price,
                "current_price": current_price,
                "profit_loss": profit_loss,
                "profit_percentage": round(profit_percentage, 2)  # 🚀 소수점 2자리 반올림
            }

        return Response({"profit_data": profit_data}, status=status.HTTP_200_OK)
