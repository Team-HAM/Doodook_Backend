from django.shortcuts import render
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

import matplotlib
matplotlib.use("Agg")  # 🚀 백엔드에서 차트 렌더링을 위한 설정

# 기존 get_stock_price()는 단순 현재가(int)를 반환하는 함수일 가능성이 높음
# 대신 Kiwoom에서 일봉 데이터를 가져오는 함수가 필요함!
from trading.utils import get_price_data  # ✅ 올바른 일봉 데이터 가져오기 함수 사용

import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from trading.utils import get_price_data  # ✅ Kiwoom API에서 데이터 가져오기

class DailyChartView(APIView):
    """ 특정 종목의 일봉 데이터를 가져와 캔들 차트로 변환 """

    permission_classes = [AllowAny]  # 🚀 인증 없이 접근 가능

    def get(self, request, stock_code):
        try:
            df = get_price_data(stock_code)  # ✅ get_price_data()로 변경

            if df is None or df.empty:
                return JsonResponse({"error": "일봉 데이터를 가져올 수 없습니다."}, status=404)

            # 🚀 데이터 변환
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)  # ✅ 날짜 변환
                print("✅ 인덱스를 datetime 형식으로 변환 완료!")

            # 🚀 이동평균선 추가 (5일, 20일, 60일)
            df["MA5"] = df["close"].rolling(window=5).mean()
            df["MA20"] = df["close"].rolling(window=20).mean()
            df["MA60"] = df["close"].rolling(window=60).mean()

            # 🚀 색상 스타일 설정 (양봉: 빨간색, 음봉: 파란색)
            mc = mpf.make_marketcolors(
                up="r", down="b", edge="inherit", wick="inherit", volume="inherit"
            )
            s = mpf.make_mpf_style(
                base_mpf_style="starsandstripes",
                marketcolors=mc,
                gridaxis="both",
                y_on_right=True,
            )

            # 🚀 차트 + 거래량을 위한 서브플롯 생성
            fig, (ax, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})

            # 🚀 캔들 차트 + 거래량 표시 + 이동평균선 추가
            mpf.plot(
                df.tail(60),  # ✅ 최근 60일 데이터만 표시
                type="candle",
                style=s,
                ax=ax,
                volume=ax2,  # ✅ 거래량 그래프 추가
                mav=(5, 20, 60),  # ✅ 이동평균선 추가
                scale_width_adjustment=dict(volume=0.8, candle=1)  # ✅ 거래량 차트 비율 추가
            )

            # 🚀 차트를 이미지로 변환하여 응답
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)

            return HttpResponse(buffer.getvalue(), content_type="image/png")

        except Exception as e:
            print(f"🚨 차트 생성 오류: {e}")  # ✅ 오류 로그 추가
            return JsonResponse({"error": str(e)}, status=500)



class DailyChartDataView(APIView):
    """ 특정 종목의 일봉 데이터를 JSON으로 반환 """

    permission_classes = [AllowAny]  # 🚀 인증 없이 접근 가능

    def get(self, request, stock_code):
        try:
            df = get_price_data(stock_code)  # ✅ get_price_data() 함수 호출

            if df is None or df.empty:
                return JsonResponse({"error": "일봉 데이터를 가져올 수 없습니다."}, status=404)

            # 🚀 날짜 데이터 변환
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            # 🚀 이동평균선 추가 (5일, 20일, 60일)
            df["MA5"] = df["close"].rolling(window=5).mean()
            df["MA20"] = df["close"].rolling(window=20).mean()
            df["MA60"] = df["close"].rolling(window=60).mean()

            # 🚀 JSON 형식으로 변환
            json_data = df.tail(60).reset_index().to_dict(orient="records")  # ✅ 최근 60일 데이터만 반환

            return JsonResponse({"stock_code": stock_code, "data": json_data}, status=200, safe=False)  # 🚀 JSON 응답

        except Exception as e:
            print(f"🚨 JSON 응답 오류: {e}")  # ✅ 오류 로그 추가
            return JsonResponse({"error": str(e)}, status=500)
