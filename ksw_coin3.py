import time
import pyupbit
import datetime
import requests

################################################
access = "5I9JQCQ21obbyno3631A2xlisGjCVgzxLw8csbDb"
secret = "qJytN9DZfS9ruxkBDyllUS7hmYBM7RvaFy9DRWS8"
stock = "xoxb-3566443758993-3574327487846-oEa7FQtbFLHYtnap3uSHGmC6"
coinN = "KRW-ETC"
tk = 0.4

################################################
def post_message(token, mystock, text):
    """슬랙 봇 연결사항"""
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": mystock, "text": text}
                             )


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=2)
    check_p = (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    target_p = df.iloc[0]['close'] + check_p
    return check_p, target_p

def get_targetB_price(ticker, k):
    """변동성 돌파 전략으로 매도 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=2)
    check_p = (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    targetB_p = df.iloc[0]['close'] - check_p
    return check_p, targetB_p


def get_close_price(ticker):
    """종가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=2)
    close_price_b = df.iloc[0]['close']
    close_price_c = df.iloc[1]['close']
    return close_price_b, close_price_c

def get_ma15(ticker):
    """15 이동평균선 값"""
    conin_OHLCV = pyupbit.get_ohlcv(ticker, interval="minute60", count=15)
    ma15 = conin_OHLCV['close'].rolling(15).mean().iloc[-1]
    ma15 = round(ma15, 1)
    return ma15


def get_ma50(ticker):
    """50 이동평균선 값"""
    conin_OHLCV = pyupbit.get_ohlcv(ticker, interval="minute60", count=50)
    ma50 = conin_OHLCV['close'].rolling(50).mean().iloc[-1]
    ma50 = round(ma50, 1)
    return ma50


def get_current_price(ticker):
    """현재가 조회-실시간"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


def get_start_time(ticker):
    """시작시간 조회"""
    conin_OHLCV = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start = conin_OHLCV.index[0].tz_localize(None)
    return start


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return b['balance']
            else:
                return 0
    return 0


################################################
upbit = pyupbit.Upbit(access, secret)
buy_check = 0
sell_check = 0
time_check = 0
cross_check = 0
post_message(stock, "#stock", "--KSW AUTO COIN-3 START--")
post_message(stock, "#stock", "%s COIN-3" % coinN)
print("--KSW AUTO COIN-3 START--")
################################################
###############2022-07-20#######################

while True:
    try:
        #start_time = get_start_time(coinN)              # 시작시간 - 사용 안함
        current_time = datetime.datetime.now()           # 현시간
        target_price = get_target_price(coinN, tk)       # 목표가(매수)
        targetB_price = get_targetB_price(coinN, tk)     # 목표가(매도)
        current_price = get_current_price(coinN)         # 현재가
        close_price = get_close_price(coinN)             # 종가
        ma15_price = get_ma15(coinN)                     # 15ma
        ma50_price = get_ma50(coinN)                     # 50ma
        korea_price = get_balance("KRW")                 # 내지갑
        sell_price = get_balance(coinN.split("-")[1])    # 내XRP


        if cross_check == 0 :
            if ma15_price > ma50_price:
                post_message(stock, "#stock", "[CHECK]\n 골드크로스구간\n P L A Y.")
                cross_check = 1
                pass
            elif ma15_price < ma50_price:
                post_message(stock, "#stock", "[CHECK]\n 데드크로스구간\n S T O P.")
                cross_check = 2
                pass

        if cross_check == 2:
            if ma15_price > ma50_price:
                post_message(stock, "#stock", "[CHECK]\n 골드크로스구간 진입--- \n 투자진행.")
                cross_check = 0
                pass

        if cross_check == 1:
            if ma15_price < ma50_price:
                post_message(stock, "#stock", "[CHECK]\n 데드크로스구간 진입--- \n 투자멈춤.")
                cross_check = 0
                pass

        if time_check == 0:
            if current_time.hour == 9:
                post_message(stock, "#stock", "[CHECK]\n 09:00 장이 시작되었습니다.")
                time_check = 1
                pass

        if current_time.hour > 9:
            time_check = 0
            pass


        ############################매수############################################
        if buy_check == 0 and cross_check == 1 :
            if 10 < current_time.minute < 30:
                if close_price[1] >= ma15_price and target_price[1] == current_price :
                    post_message(stock, "#stock",
                                "[TARGET-PRICE]\n CV-K : %s\n TP : %s\n CP : %s" % (target_price[0],
                                                                                    target_price[1],
                                                                                    current_price))
                    if float(korea_price) > 5000:
                        buy_result = upbit.buy_market_order(coinN, float(korea_price) * 0.9995)
                        post_message(stock, "#stock","[BUY]\n %s \n Current Price : %s" % (coinN, current_price))
                        buy_check = 1
                    else:
                        post_message(stock, "#stock", "[NO-MONEY]")

        ############################매도############################################
        if buy_check == 1:
            if 45 < current_time.minute < 50 :
                if close_price[1] > ma15_price :
                    if sell_check == 0:
                        post_message(stock, "#stock", "[CHECK]\n H O L D C O I N")
                        sell_check = 1
                        pass
                elif close_price[1] < ma15_price :
                    if float(sell_price) > 0.0008:
                        sell_result = upbit.sell_market_order(coinN, float(sell_price) * 0.9995)
                        post_message(stock, "#stock", "[SELL]\n %s \n SELL PRICE : %s"
                                     % (sell_result['market'], current_price))

                        sell_check = 0
                        buy_check = 0
                        cross_check = 0

                    time.sleep(5)
                    post_message(stock, "#stock", "[CHECK]\n --NEW CHECK COIN-3 START--")
    except Exception as e:
        if str(e) == "'NoneType' object is not subscriptable":
            pass
        else:
            print("ERROR NAME  :  %s" % e)
            post_message(stock, "#stock", "[ERROR NAME] : %s" % e)

        time.sleep(3)
