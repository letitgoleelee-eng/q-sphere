키움증권 REST API (키움 OpenAPI+ REST 서비스) 를 사용해
주식 시세조회 및 매매 자동화 솔루션 구축




---

🧭 전체 구성 개요

[GCP Windows VM]
   ├─ Python 3
   ├─ Kiwoom REST API (인증키 기반)
   ├─ 자동매매 코드 (시세조회 + 주문)
   ├─ 스케줄러 or Flask 백엔드
   └─ 로그 저장 / 알림 전송


---

1️⃣ 키움 REST API 개념 정리

기존 OpenAPI+ (ActiveX 기반) 은 Windows GUI 기반이었죠.
하지만 2023년부터 REST API (HTTP 기반) 도 제공됩니다.

👉 장점:

서버 환경에서 동작 가능 (Windows/Linux 가능)

로그인 창 불필요 (OAuth2 토큰 인증)

JSON 응답으로 쉽게 처리 가능



---

2️⃣ 사전 준비

✅ ① 키움증권 계좌 개설 및 인증

키움증권 홈페이지

HTS 영웅문 → OpenAPI 신청

“OpenAPI 서비스 → REST API 이용 신청” 클릭
(관리자 승인 후 API Key 발급)


✅ ② 발급 정보 확인

AppKey

AppSecret

계좌번호

(테스트용이면 모의투자 계좌 가능)



---

3️⃣ GCP Windows VM 환경 설정

1️⃣ Python 설치

winget install Python.Python.3.10

2️⃣ 필요한 라이브러리 설치

pip install requests flask pandas

3️⃣ API 호출 테스트용 폴더 생성

mkdir C:\kiwoom_rest_bot
cd C:\kiwoom_rest_bot


---

4️⃣ 키움 REST API 기본 구조

📡 REST API는 다음 형태로 동작합니다.

기능	메서드	엔드포인트

토큰 발급	POST	/oauth2/tokenP
시세조회	GET	/uapi/domestic-stock/v1/quotations/inquire-price
주문	POST	/uapi/domestic-stock/v1/trading/order-cash



---

5️⃣ 인증 토큰 발급 코드

import requests
import json

APP_KEY = "발급받은_APP_KEY"
APP_SECRET = "발급받은_APP_SECRET"

url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
headers = {"content-type": "application/json"}
body = {
    "grant_type": "client_credentials",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET
}

res = requests.post(url, headers=headers, data=json.dumps(body))
token = res.json()["access_token"]
print("Access Token:", token)

> 💡 토큰 유효시간은 보통 24시간.
자동으로 재발급되도록 설정하는 것이 좋습니다.




---

6️⃣ 시세조회 (예: 삼성전자 현재가)

import requests

ACCESS_TOKEN = token  # 위에서 발급받은 토큰 사용

url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET,
    "tr_id": "FHKST01010100"  # 주식현재가조회
}
params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"}

res = requests.get(url, headers=headers, params=params)
data = res.json()
print("삼성전자 현재가:", data["output"]["stck_prpr"])


---

7️⃣ 주문 (매수/매도)

url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/order-cash"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET,
    "tr_id": "TTTC0802U",  # 매수: TTTC0802U, 매도: TTTC0801U
}

body = {
    "CANO": "12345678",           # 계좌번호 앞 8자리
    "ACNT_PRDT_CD": "01",         # 계좌상품코드 (보통 01)
    "PDNO": "005930",             # 종목코드
    "ORD_DVSN": "00",             # 00: 지정가, 01: 시장가
    "ORD_QTY": "10",              # 수량
    "ORD_UNPR": "70000"           # 주문단가
}

res = requests.post(url, headers=headers, data=json.dumps(body))
print(res.json())


---

8️⃣ Flask 서버로 자동화 제어 예시

from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route("/price/<code>")
def get_price(code):
    # 위의 시세조회 함수 호출
    price = inquire_price(code)
    return jsonify({"code": code, "price": price})

@app.route("/buy/<code>/<qty>")
def buy(code, qty):
    result = order_cash(code, qty, price="70000", order_type="buy")
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

이렇게 하면
👉 브라우저에서 http://<GCP_IP>:8080/price/005930 으로
삼성전자 현재가를 바로 확인할 수 있습니다.


---

9️⃣ 자동매매 로직 예시

if float(data["output"]["stck_prpr"]) < 65000:
    order_cash("005930", 10, "65000", "buy")
elif float(data["output"]["stck_prpr"]) > 75000:
    order_cash("005930", 10, "75000", "sell")


---

🔒 10️⃣ 실전 운영 팁

🔁 토큰 자동 갱신 (매일 오전 8:50에 스케줄러로)

🧾 로그 저장 (logging 모듈 사용)

🚨 예외 처리 (API 실패 시 재시도)

🧠 모의투자로 충분히 검증 후 실계좌 전환



---

✅ 전체 정리 요약

단계	내용	명령 / 코드

1	GCP Windows VM 생성	Compute Engine
2	Python 설치	winget install Python.Python.3.10
3	라이브러리 설치	pip install requests flask pandas
4	API 신청	키움 OpenAPI → REST API 신청
5	토큰 발급	/oauth2/tokenP
6	시세조회	/uapi/domestic-stock/v1/quotations/inquire-price
7	매수/매도 주문	/uapi/domestic-stock/v1/trading/order-cash
8	Flask로 API 서버 구성	/price/<code> /buy/<code>/<qty>
9	자동매매 조건 로직	if-else 기반 전략
10	실운영 및 백업	스케줄러 + 로깅






