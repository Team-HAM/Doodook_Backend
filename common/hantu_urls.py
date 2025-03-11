#!/usr/bin/env python
"""
urls for 한투 API
"""

####################### 한투 API 관련 상수 시작 #######################
ONL_API_URL_BASE = "https://openapi.koreainvestment.com:9443"
TST_API_URL_BASE = "https://openapivts.koreainvestment.com:29443" #모의투자서비스

ONL_WS_URL_BASE = "ws://ops.koreainvestment.com:21000"
TST_WS_URL_BASE = "ws://ops.koreainvestment.com:31000"

STOCK_PRICE_API = "/uapi/domestic-stock/v1/quotations/inquire-price"

#### OAuth 인증 API
OAUTH_TOKEN_ISSUE = "/oauth2/Approval"       # POST / 실시간 (웹소켓) 접속키 발급[실시간-000]
HASHKEY = "/uapi/hashkey"                    # POST / Hashkey
ACCESS_TOKEN_ISSUE = "/oauth2/tokenP"        # POST / 접근토큰발급(P)[인증-001]
ACCESS_TOKEN_DESTROY = "/oauth2/revokeP"     # POST / 접근토큰폐기(P)[인증-002]

#### [국내주식] 주문/계좌
TRX_ORDER_KO_STOCK_CASH = "/uapi/domestic-stock/v1/trading/order-cash" # POST / 주식주문(현금)[v1_국내주식-001]
TRX_ORDER_KO_STOCK_CRDT = "/uapi/domestic-stock/v1/trading/order-credit" # POST / 주식주문(신용)[v1_국내주식-002] / 모의투자 미지원
TRX_ORDER_KO_STOCK_MOD = "/uapi/domestic-stock/v1/trading/order-rvsecncl" # POST / 주식주문(정정취소)[v1_국내주식-003]
...
####################### 한투 API 관련 상수 끝  #######################