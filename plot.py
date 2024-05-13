import ccxt
import requests
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
# os.chdir('/root/btcfuturedata')

delists = [
    "SRM",
    "HNT",
    "TOMO",
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

def figure_plot(filename, symbol, basepath="./figures/"):
    # visualize the data in the csv file using pandas
    pdata = pd.read_csv(filename)
    pdata['timestamp'] = pd.to_datetime(pdata['timestamp'], unit='ms')
    pdata.set_index('timestamp', inplace=True)
    pdata["volume"] = pdata["sellVol"]+pdata["buyVol"]

    # 合约持仓
    openInterestHist="sumOpenInterest,sumOpenInterestValue".split(',')
    openInterestHist.append("volume")
    openInterestHist.append("closePrice")

    plt.figure()
    pdata[openInterestHist].plot(subplots=True)
    plt.savefig(basepath+symbol+'.png', dpi=300)


    # # 大户账户多空比
    # plt.figure()
    # topLongShortAccountRatio="topacclongShortRatio,toplongAccount,topshortAccount".split(',')
    # pdata[topLongShortAccountRatio].plot(subplots=True)
    # plt.savefig(basepath+symbol+'_topLongShortAccountRatio.png', dpi=300)
    # # 大户持仓量多空比
    # plt.figure()
    # topLongShortPositionRatio="topposlongShortRatio,longPosition,shortPosition".split(',')
    # pdata[topLongShortPositionRatio].plot(subplots=True)
    # plt.savefig(basepath+symbol+'_topLongShortPositionRatio.png', dpi=300)
    # # 多空持仓人数比
    # plt.figure()
    # globalLongShortAccountRatio="globallongShortRatio,globallongAccount,globalshortAccount".split(',')
    # pdata[globalLongShortAccountRatio].plot(subplots=True)
    # plt.savefig(basepath+symbol+'_globalLongShortAccountRatio.png', dpi=300)



symbolist = []
exchange = ccxt.binance({
    'apiKey': '',
    'secret': '',
    'enableRateLimit': True,  # 启用请求限制
    'options': {
        'defaultType': 'future'
    }
})


csvs = os.listdir('./csvs_merge')
for csv in csvs:
    symbol = csv.split('.')[0]
    f = os.path.join('./csvs_merge', csv)
    data = pd.read_csv(f)
    figure_plot(f, symbol)

