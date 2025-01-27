import sys
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop

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

if __name__ == "__main__":
    stock_code = "005930"  # 예: 삼성전자
    api = KiwoomAPI()
    price = api.get_current_price(stock_code)
    print(f"현재 주식 가격({stock_code}): {price}")
