from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop
import sys
import pandas as pd

class KiwoomAPI:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.event_loop = QEventLoop()
        self.kiwoom.OnEventConnect.connect(self._on_login)
        self.kiwoom.dynamicCall("CommConnect()")  # 로그인 요청
        self.event_loop.exec_()

        self.price = None  # ✅ 초기화 (이전 요청 값 저장 방지)
        self.df = None  # ✅ 일봉 데이터 저장용 변수

    def _on_login(self, err_code):
        if err_code == 0:
            print("Kiwoom API 로그인 성공")
        else:
            print(f"Kiwoom API 로그인 실패, 에러 코드: {err_code}")
        self.event_loop.quit()

    def get_current_price(self, stock_code):
        """ 특정 종목의 현재가 조회 """
        try:
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식현재가요청", "opt10001", 0, "0101")

            self.event_loop = QEventLoop()
            self.kiwoom.OnReceiveTrData.connect(self._on_receive_tr_data)
            self.event_loop.exec_()

            if self.price is None:
                raise ValueError(f"주식 코드 '{stock_code}'에 대한 가격 조회 실패.")

            return abs(self.price)  # ✅ 절대값으로 변환하여 부호 문제 해결

        except Exception as e:
            print(f"주식 가격 조회 오류: {e}")
            raise Exception(f"주식 가격 조회 중 오류가 발생했습니다: {str(e)}")

    def get_price_data(self, stock_code):
        """ 특정 종목의 일봉 데이터 조회 (캔들 차트 용도) """
        try:
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", "20240101")  # 기준일 설정 (예: 2024년 1월 1일)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")  # 수정주가 반영 여부

            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "일봉차트조회", "opt10081", 0, "0101")

            self.event_loop = QEventLoop()
            self.kiwoom.OnReceiveTrData.connect(self._on_receive_candle_data)
            self.event_loop.exec_()

            if self.df is None or self.df.empty:
                raise ValueError(f"주식 코드 '{stock_code}'의 일봉 데이터 조회 실패.")

            return self.df

        except Exception as e:
            print(f"일봉 데이터 조회 오류: {e}")
            return None

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, prev_next, data_len, err_code, msg1, msg2):
        """ 현재가 조회 이벤트 핸들러 """
        if rqname == "주식현재가요청":
            try:
                price_str = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, 0, "현재가").strip()
                if not price_str:
                    raise ValueError(f"주식 가격 조회 실패: {msg1} - {msg2}")
                self.price = int(price_str)
            except ValueError as e:
                print(f"주식 가격 조회 오류: {e}")
                self.price = None  
            except Exception as e:
                print(f"예상치 못한 오류 발생: {e}")
                self.price = None
            finally:
                self.event_loop.quit()

    def _on_receive_candle_data(self, screen_no, rqname, trcode, record_name, prev_next, data_len, err_code, msg1, msg2):
        """ 일봉 데이터 조회 이벤트 핸들러 """
        if rqname == "일봉차트조회":
            try:
                data = []
                for i in range(10):  # 최근 10개의 일봉 데이터 가져오기
                    date = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, i, "일자").strip()
                    open_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, i, "시가").strip()
                    high_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, i, "고가").strip()
                    low_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, i, "저가").strip()
                    close_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, i, "현재가").strip()
                    volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, record_name, i, "거래량").strip()

                    # 🚀 date 값이 정상적으로 들어오는지 확인
                    print(f"Row {i}: date={date}, open={open_price}, high={high_price}, low={low_price}, close={close_price}, volume={volume}")

                    # 🚨 빈 값이거나 숫자로 변환할 수 없는 데이터 확인
                    if not date or not open_price or not high_price or not low_price or not close_price or not volume:
                        print(f"🚨 데이터 누락! {date}, {open_price}, {high_price}, {low_price}, {close_price}, {volume}")
                        continue  # 데이터가 없는 경우 해당 행은 건너뛰기

                    # 🚀 정수로 변환 (부호 문제 해결)
                    data.append([date, abs(int(open_price)), abs(int(high_price)), abs(int(low_price)), abs(int(close_price)), int(volume)])

                self.df = pd.DataFrame(data, columns=["date", "open", "high", "low", "close", "volume"])
                print("🚀 생성된 DataFrame:")
                print(self.df.head())  # ✅ DataFrame이 정상적으로 생성되는지 확인!

                # 🚀 날짜 변환 및 인덱스 설정
                self.df["date"] = pd.to_datetime(self.df["date"], format="%Y%m%d")  # ✅ 날짜 변환
                self.df.set_index("date", inplace=True)  # ✅ 날짜를 인덱스로 설정
                print("✅ 변환된 DataFrame (Index: date):")
                print(self.df.head())  # ✅ 최종 변환된 데이터 확인!

            except Exception as e:
                print(f"일봉 데이터 변환 오류: {e}")
                self.df = None
            finally:
                self.event_loop.quit()



# ✅ 현재가 조회 함수
def get_stock_price(stock_code):
    try:
        api = KiwoomAPI()
        return api.get_current_price(stock_code)
    except Exception as e:
        print(f"주식 가격 조회 오류: {e}")
        return None

# ✅ 일봉 데이터 조회 함수 (차트용)
def get_price_data(stock_code):
    try:
        api = KiwoomAPI()
        return api.get_price_data(stock_code)
    except Exception as e:
        print(f"일봉 데이터 조회 오류: {e}")
        return None
