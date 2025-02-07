from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop
import sys

class KiwoomAPI:
    def __init__(self):
        self.app = QApplication(sys.argv)
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
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식현재가요청", "opt10001", 0, "0101")

            self.event_loop = QEventLoop()
            self.kiwoom.OnReceiveTrData.connect(self._on_receive_tr_data)
            self.event_loop.exec_()

            if self.price is None:
                raise ValueError(f"주식 코드 '{stock_code}'에 대한 가격 조회 실패.")

            return self.price

        except Exception as e:
            print(f"주식 가격 조회 오류: {e}")
            raise Exception(f"주식 가격 조회 중 오류가 발생했습니다: {str(e)}")

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, prev_next, data_len, err_code, msg1, msg2):
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


def get_stock_price(stock_code):
    try:
        api = KiwoomAPI()
        price = api.get_current_price(stock_code)
        return abs(price)  # ✅ 절대값으로 변환하여 부호 문제 해결
    except Exception as e:
        print(f"주식 가격 조회 오류: {e}")
        return None

