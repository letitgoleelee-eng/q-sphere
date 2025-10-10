#주문 (매수/매도)
#Windows 환경 + 영웅문4 설치된 PC 에서만 작동합니다.
#(GCP Windows Server에서도 가능하지만, GUI 로그인 필요)

#로그인 창이 팝업으로 뜨므로 RDP(원격접속) 상태에서 실행해야 합니다.

#영웅문을 모의투자 모드로 로그인해야 모의주문이 가능합니다.

#시장가로 주문하려면 "hoga": "03", price=0 으로 설정

# url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/order-cash" headers = { "Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}", "appkey": APP_KEY, "appsecret": APP_SECRET, "tr_id": "TTTC0802U", # 매수: TTTC0802U, 매도: TTTC0801U } body = { "CANO": "12345678", # 계좌번호 앞 8자리 "ACNT_PRDT_CD": "01", # 계좌상품코드 (보통 01) "PDNO": "005930", # 종목코드 "ORD_DVSN": "00", # 00: 지정가, 01: 시장가 "ORD_QTY": "10", # 수량 "ORD_UNPR": "70000" # 주문단가 } res = requests.post(url, headers=headers, data=json.dumps(body)) print(res.json())
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget

class KiwoomAPI:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")  # 키움 OpenAPI 컨트롤
        self.ocx.OnEventConnect.connect(self._event_connect)
        self.ocx.OnReceiveTrData.connect(self._receive_tr_data)
        self.login_event_loop = None
        self.tr_event_loop = None
        self.data = None

    def _event_connect(self, err_code):
        if err_code == 0:
            print("✅ 로그인 성공")
        else:
            print("❌ 로그인 실패")
        self.login_event_loop.exit()

    def login(self):
        self.ocx.dynamicCall("CommConnect()")
        from PyQt5.QtCore import QEventLoop
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _receive_tr_data(self, scr_no, rqname, trcode, recordname, prev_next):
        print("TR 데이터 수신 완료")
        self.tr_event_loop.exit()

    def get_account(self):
        accounts = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        return accounts.split(';')[0]  # 첫 번째 계좌

    def send_order(self, rqname, scr_no, acc_no, order_type, code, qty, price, hoga, org_order_no):
        """
        order_type:
         - 1 : 매수
         - 2 : 매도
         - 3 : 매수취소
         - 4 : 매도취소
        hoga:
         - "00" : 지정가
         - "03" : 시장가
        """
        ret = self.ocx.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            [rqname, scr_no, acc_no, order_type, code, qty, price, hoga, org_order_no]
        )
        if ret == 0:
            print("📨 주문 전송 성공")
        else:
            print("⚠️ 주문 전송 실패 (코드:", ret, ")")

        from PyQt5.QtCore import QEventLoop
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

if __name__ == "__main__":
    kiwoom = KiwoomAPI()
    kiwoom.login()

    account = kiwoom.get_account()
    print("계좌번호:", account)

    # 예시: 삼성전자(005930) 10주 매수 (지정가 70,000원)
    kiwoom.send_order(
        rqname="매수주문",
        scr_no="0101",
        acc_no=account,
        order_type=1,       # 1: 매수
        code="005930",      # 종목코드
        qty=10,             # 수량
        price=70000,        # 주문단가
        hoga="00",          # 지정가
        org_order_no=""     # 신규 주문이므로 빈칸
    )
