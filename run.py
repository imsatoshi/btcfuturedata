import os
import requests
import pbinance
import pytz
import pandas as pd
import datetime
import ccxt
import matplotlib.pyplot as plt
from git import Repo

cols = "timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,topposlongShortRatio,longPosition,shortPosition,globallongShortRatio,globallongAccount,globalshortAccount,buySellRatio,sellVol,buyVol,openPrice,highPrice,lowPrice,closePrice".split(",")
delists = [
    "SRM",
    "SLP",
    "HNT",
    "TOMO",
    "USDC",
    "CVC",
    "CTK",
    "BTS",
    "BTCST",
    "SC",
    "DGB",
    "RAY",
    "ANT",
    "FTT",
    "FOOTBALL",
    "BLUEBIRD",
    "COCOS",
    "STRAX"
]


def write_data(symbol, subpath="csvs", period="5m", limit=100):
    timestamps = set()
    binance = pbinance.Binance("", "")
    filename = "./{}/{}.csv".format(subpath, symbol)
    existing_timestamps = []
    if os.path.exists(filename):
        pdata = pd.read_csv(filename)
        non_null_rows = pdata[pdata.notna().all(axis=1)]
        existing_timestamps = non_null_rows["timestamp"].tolist()
    else:
        pdata = pd.DataFrame(columns='timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,topposlongShortRatio,longPosition,shortPosition,globallongShortRatio,globallongAccount,globalshortAccount,buySellRatio,sellVol,buyVol,openPrice,highPrice,lowPrice,closePrice'.split(","))
    max_sumopeninterestvalue = pdata["sumOpenInterestValue"].max()
    maxTopLongShortAccountRatio = pdata["topacclongShortRatio"].max()
    maxTopLongShortPositionRatio = pdata["topposlongShortRatio"].max()
    maxGlobalLongShortAccountRatio = pdata["globallongShortRatio"].max()
    openInterestHist = binance.um.market.get_openInterestHist(symbol=symbol, period=period, limit=limit)
    openInterestHistMap = {}
    for tmp in openInterestHist["data"]:
        openInterestHistMap[tmp["timestamp"]]=tmp
        if tmp["timestamp"] not in existing_timestamps:
            timestamps.add(tmp["timestamp"])

    topLongShortAccountRatio = binance.um.market.get_topLongShortAccountRatio(symbol=symbol, period=period, limit=limit)
    topLongShortAccountRatioMap = {}
    for tmp in topLongShortAccountRatio["data"]:
        topLongShortAccountRatioMap[tmp["timestamp"]]=tmp
        if tmp["timestamp"] not in existing_timestamps:
            timestamps.add(tmp["timestamp"])

    topLongShortPositionRatio = binance.um.market.get_topLongShortPositionRatio(symbol=symbol, period=period, limit=limit)
    topLongShortPositionRatioMap = {}
    for tmp in topLongShortPositionRatio["data"]:
        topLongShortPositionRatioMap[tmp["timestamp"]]=tmp
        if tmp["timestamp"] not in existing_timestamps:
            timestamps.add(tmp["timestamp"])

    globalLongShortAccountRatio = binance.um.market.get_globalLongShortAccountRatio(symbol=symbol, period=period, limit=limit)
    globalLongShortAccountRatioMap = {}
    for tmp in globalLongShortAccountRatio["data"]:
        globalLongShortAccountRatioMap[tmp["timestamp"]]=tmp
        if tmp["timestamp"] not in existing_timestamps:
            timestamps.add(tmp["timestamp"])

    takerlongshortRatio = binance.um.market.get_takerlongshortRatio(symbol=symbol, period=period,limit=limit)
    takerlongshortRatioMap = {}
    for tmp in takerlongshortRatio["data"]:
        takerlongshortRatioMap[tmp["timestamp"]]=tmp
        if tmp["timestamp"] not in existing_timestamps:
            timestamps.add(tmp["timestamp"])

    prices = binance.um.market.get_markPriceKlines(symbol=symbol, interval=period, limit=limit)
    pricesMap = {}
    for tmp in prices["data"]:
        pricesMap[tmp[0]]=tmp
        if tmp[0] not in existing_timestamps:
            timestamps.add(tmp[0])
    
    if len(timestamps) > 0:
        new_rows = []
        for tst in sorted(timestamps):
            new_rows.append({"timestamp": tst})
        pdata = pdata._append(new_rows, ignore_index=True)
    
    pdata = pdata.sort_values("timestamp", ascending=True)


    for tms in timestamps:
        if openInterestHistMap.get(tms, None) is not None:
            oi = openInterestHistMap[tms]
            # 合约持仓, 合约持仓价值
            pdata.loc[pdata['timestamp']==tms, ["sumOpenInterest", "sumOpenInterestValue"]] = [oi["sumOpenInterest"], oi["sumOpenInterestValue"]]

        if topLongShortAccountRatioMap.get(tms, None) is not None:
            oi = topLongShortAccountRatioMap[tms]
            #  大户人数多空比, 大户多头占比，空头占比
            pdata.loc[pdata['timestamp']==tms, ["topacclongShortRatio", "toplongAccount", "topshortAccount"]] = [oi["longShortRatio"], oi["longAccount"], oi["shortAccount"]]

        if topLongShortPositionRatioMap.get(tms, None) is not None:
            oi = topLongShortPositionRatioMap[tms]
            # 大户持仓多空比， 大户持仓多头占比，大户持仓空投占比 topposlongShortRatio,longPosition,shortPosition
            pdata.loc[pdata['timestamp']==tms, ["topposlongShortRatio", "longPosition", "shortPosition"]] = [oi["longShortRatio"], oi["longAccount"], oi["shortAccount"]]

        if globalLongShortAccountRatioMap.get(tms, None) is not None:
            oi = globalLongShortAccountRatioMap[tms]
            # 全网多空持仓人数比, 多头占比， 空头占比 globallongShortRatio,globallongAccount,globalshortAccount
            pdata.loc[pdata['timestamp']==tms, ["globallongShortRatio", "globallongAccount", "globalshortAccount"]] = [oi["longShortRatio"], oi["longAccount"], oi["shortAccount"]]

        if takerlongshortRatioMap.get(tms, None) is not None:
            oi = takerlongshortRatioMap[tms]
            #合约主动买卖量  buySellRatio,sellVol,buyVol
            pdata.loc[pdata['timestamp']==tms, ["buySellRatio", "sellVol", "buyVol"]] = [oi["buySellRatio"], oi["sellVol"], oi["buyVol"]]

        if pricesMap.get(tms, None) is not None:
            oi = pricesMap[tms]
            # 合约价格，开仓、高、低、关 openPrice,highPrice,lowPrice,closePrice
            pdata.loc[pdata['timestamp']==tms, ["openPrice", "highPrice", "lowPrice", "closePrice"]] = [oi[1], oi[2], oi[3], oi[4]]

    pdata[cols].to_csv(filename)

    last_data = pdata.iloc[-1]
    # check last_data sumOpenInterestVale 是不是nan
    if pd.isna(last_data["sumOpenInterestValue"]):
        last_data = pdata.iloc[-2]
    flagSumOpenInterestValue = float(last_data["sumOpenInterestValue"]) > float(max_sumopeninterestvalue)  # 市值

    # last_data = pdata.iloc[-1]
    # if pd.isna(last_data["topacclongShortRatio"]):
        # last_data= pdata.iloc[-2]
    # flagTopacclongShortRatio = float(last_data["topacclongShortRatio"]) > float(maxTopLongShortPositionRatio)   # 大户多空比
    # last_data = pdata.iloc[-1]
    # if pd.isna(last_data["topposlongShortRatio"]):
        # last_data= pdata.iloc[-2]
    # flagTopposlongShortRatio = float(last_data["topposlongShortRatio"]) > float(maxTopLongShortPositionRatio)     # 大户持仓多空比

    last_data = pdata.iloc[-1]
    if pd.isna(last_data["globallongShortRatio"]):
        last_data= pdata.iloc[-2]
    flagGloballongShortRatio = float(last_data["globallongShortRatio"]) > float(maxGlobalLongShortAccountRatio)     # 全局多空比
    
    return flagSumOpenInterestValue, flagGloballongShortRatio
    # return flagSumOpenInterestValue, flagTopacclongShortRatio, flagTopposlongShortRatio, flagGloballongShortRatio


if __name__ == "__main__":
    symbolist = []
    exchange = ccxt.binance({
        'apiKey': '',
        'secret': '',
        'enableRateLimit': True,  # 启用请求限制
        'options': {
            'defaultType': 'future'
        }
    })
    symbols = []
    markets = exchange.load_markets()
    newHighList = [] 
    for m in markets:
        if m.endswith("/USDT:USDT"):
            symbols.append(m)
            s = m.split("/")[0]
            symbol = m.split("/")[0]+"USDT"
            flag = False
            for delist in delists:
                if delist in symbol:
                    flag = True
            if flag:
                continue
            # flagSumOpenInterestValue, flagTopacclongShortRatio, flagTopposlongShortRatio, flagGloballongShortRatio = write_data(symbol, subpath="csvs", limit=10)
            flagSumOpenInterestValue, flagGloballongShortRatio = write_data(symbol, subpath="csvs", limit=10)
            if flagSumOpenInterestValue:
                newHighList.append(symbol+"-市值")
            # if flagTopacclongShortRatio:
                # newHighList.append(symbol+"-大户多空比")
            # if flagTopposlongShortRatio:
                # newHighList.append(symbol+"-大户持仓多空比")
            if flagGloballongShortRatio:
                newHighList.append(symbol+"-全网多空比")

    tz = pytz.timezone('Asia/Shanghai')
    for s in newHighList:
        print(s)
        message = ""
        data = pd.read_csv("./csvs/{}.csv".format(s.split("-")[0]))
        last_data = data.iloc[-1]

        for c in cols:
            if c == "timestamp":
                timestamp = int(float(last_data[c])) / 1000
                dt = datetime.datetime.fromtimestamp(timestamp)
                utc8_dt = dt.astimezone(tz)
                utc8_time_str = utc8_dt.strftime('%Y-%m-%d %H:%M:%S')
                message += "{}:\t{}\n".format("time", utc8_time_str)
            else:
                message += "{}:\t{}\n".format(c, last_data[c])
        # requests.post("https://api.day.app/Rn4sQCRDQr3TYNaBuKoGZe/{}/{}".format(s, message))
    repo_path = '/root/btcfuturedata'
    repo = Repo(repo_path)
    repo.git.add(all=True)
    repo.git.commit("-m", "auto submit!!!")
    repo.git.push()

