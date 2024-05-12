import requests
import os
import pbinance

   
def write_to_csv():
    symbol = "BTCUSDT"
    period = "5m"
    limit = "100"
    # contract="PERPETUAL"

    contract="ALL"

    params = {
        "pair": symbol,
        "contractType": contract,
        "period": period,
        "limit": limit
    }


    csvMap = {
        # 合约持仓量
        "openInterestHist": f'https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period={period}&limit={limit}',
        # 大户账户多空比
        "topLongShortAccountRatio": f'https://fapi.binance.com/futures/data/topLongShortAccountRatio?symbol={symbol}&period={period}&limit={limit}',
        # 大户持仓量多空比
        "topLongShortPositionRatio": f'https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol={symbol}&period={period}&limit={limit}',
        # 多空持仓人数比
        "globalLongShortAccountRatio": f'https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period={period}&limit={limit}',
        # 基差
        "basis": f'https://fapi.binance.com/futures/data/basis?pair={symbol}&contractType={contract}&period={period}&limit={limit}',
        "takerbuy": f"https://dapi.binance.com/futures/data/takerBuySellVol?pair={symbol}&contractType={contract}&period={period}" # &limit={limit}"

    }

    # curl --request GET \
    #  --url 'https://open-api-v3.coinglass.com/api/futures/takerBuySellVolume/history?exchange=Binance&symbol=BTCUSDT&interval=h1' \
    #  --header 'accept: application/json'


        


key=""
secret=""
binance = pbinance.Binance(key, secret)
t = binance.um.market.get_time()

symbol = "DASHUSDT"
openInterestHist = binance.um.market.get_openInterestHist(symbol=symbol, period='5m', limit=10)

start_time = openInterestHist["data"][0]["timestamp"]
end_time = openInterestHist["data"][-1]["timestamp"]
print(start_time, end_time)

topLongShortAccountRatio = binance.um.market.get_topLongShortAccountRatio(symbol=symbol, period='5m', limit=10)

start_time = topLongShortAccountRatio["data"][0]["timestamp"]
end_time = topLongShortAccountRatio["data"][-1]["timestamp"]
print(start_time, end_time)

topLongShortPositionRatio = binance.um.market.get_topLongShortPositionRatio(symbol=symbol, period='5m', limit=10)

start_time = topLongShortPositionRatio["data"][0]["timestamp"]
end_time = topLongShortPositionRatio["data"][-1]["timestamp"]
print(start_time, end_time)

globalLongShortAccountRatio = binance.um.market.get_globalLongShortAccountRatio(symbol=symbol, period='5m', limit=10)

start_time = globalLongShortAccountRatio["data"][0]["timestamp"]
end_time = globalLongShortAccountRatio["data"][-1]["timestamp"]
print(start_time, end_time)

takerlongshortRatio = binance.um.market.get_takerlongshortRatio(symbol=symbol, period='5m',limit=9)

start_time = takerlongshortRatio["data"][0]["timestamp"]
end_time = takerlongshortRatio["data"][-1]["timestamp"]
print(start_time, end_time)


prices = binance.um.market.get_markPriceKlines(symbol=symbol, interval="5m", limit=10)  #  startTime=start_time-6*60*100, endTime=end_time)
start_time = prices["data"][0][0]
end_time = prices["data"][-1][0]
print(start_time, end_time)



