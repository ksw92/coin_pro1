import datetime
import pyupbit
import requests
import matplotlib.pyplot as plt
import time

# 변수
access = "your-access"
secret = "your-secret"
mystock = "xoxb-3566443758993-3550928334533-CnKlrApAFl1JbVPhi6A1Mapd"


# #################

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )


# 시작시간 조회 (일봉)
def get_start_time(ticker):
    conin_OHLCV = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = conin_OHLCV.index[0]
    return start_time


# 현재가 조회
def get_current_price(ticker):
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


# 잔고 조회
def get_balance(ticker):
    balances = upbit.get_balances()
    post_message(mystock, "#stock", "잔액 : %s" % balances)
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return b['balance']
            else:
                return 0
    return 0


# 15일 이동평균선 (30분봉)
def get_ma15(ticker):
    conin_OHLCV = pyupbit.get_ohlcv(ticker, interval="minute30", count=15)
    ma15 = conin_OHLCV['close'].rolling(15).mean().iloc[-1]
    ma15 = round(ma15, 1)
    return ma15


# 50일 이동평균선 (30분봉)
def get_ma50(ticker):
    conin_OHLCV = pyupbit.get_ohlcv(ticker, interval="minute30", count=50)
    ma50 = conin_OHLCV['close'].rolling(50).mean().iloc[-1]
    ma50 = round(ma50, 1)
    return ma50


# 차트 확인 ##사용하지않음
def get_chart(ticker):
    conin_OHLCV = pyupbit.get_ohlcv(ticker, interval="minute30", count=100)
    conin_OHLCV["15"] = conin_OHLCV['close'].rolling(15).mean().iloc[-1]
    conin_OHLCV["50"] = conin_OHLCV['close'].rolling(50).mean().iloc[-1]
    conin_OHLCV[['close', '15', '50']].plot(figsize=(12, 6))
    plt.show()
    return 0


upbit = pyupbit.Upbit("")
now = datetime.datetime.now()
print("[%s] - AUTO UPBIT START" % now.strftime("%Y-%m-%d"))
post_message(mystock, "#stock", "[%s] - AUTO UPBIT START" % now.strftime("%Y-%m-%d"))
buy_check = 0

while True:
    try:
        ma15_price = get_ma15("KRW-XRP")
        current_price = get_current_price("KRW-XRP")
        ma50_price = get_ma50("KRW-XRP")

        print("확인15 : %s, 현재가 : %s, 확인50 : %s" % (ma15_price, current_price, ma50_price))

        if buy_check == 0:
            if ma15_price == ma50_price:
                if current_price > ma15_price:
                    krw_money = get_balance("KRW")
                    if krw_money > 5000:
                        print("<< JACKPOT [ALL BUY] >>")
                        buy_result = upbit.buy_market_order("KRW-XRP", krw_money * 0.9995)
                        post_message(mystock, "#stock", "<< JACKPOT [ALL BUY] >> : " + str(buy_result))
                        buy_check = 1
                    else:
                        print("NO MONEY")
                        post_message(mystock, "#stock", "<< JACKPOT [NO MONEY] >> : ")

        if buy_check == 1:
            if current_price > ma15_price:
                print("<< JACKPOT [JONBEO] >>")

            if current_price == ma15_price:
                xrp = get_balance("XRP")
                if xrp > 0.00008:
                    print("<< JACKPOT [ALL SELL] >>")
                    sell_result = upbit.sell_market_order("KRW-XRP", xrp * 0.9995)
                    post_message(mystock, "#stock", "<< JACKPOT [ALL SELL] >> : " + str(sell_result))
                    buy_check = 0
                time.sleep(10)

    except Exception as e:
        print("ERROR NAME  :  %s" % e)
        time.sleep(3)
        # exit()















