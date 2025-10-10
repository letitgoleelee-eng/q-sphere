#koreainvest.py

####실행 nginx
#pip install requests
#python koreainvest.py

####성공시 출력
#Access Token: xxxxxxxx
#삼성전자 현재가: 70300

import requests
import json

APP_KEY = "여기에_APP_KEY_입력"
APP_SECRET = "여기에_APP_SECRET_입력"

# 1️⃣ 인증 토큰 발급
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

# 2️⃣ 시세조회 (삼성전자)
ACCESS_TOKEN = token
url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET,
    "tr_id": "FHKST01010100"
}
params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"}

res = requests.get(url, headers=headers, params=params)
data = res.json()
print("삼성전자 현재가:", data["output"]["stck_prpr"])
