import sys
import ccxt
import matplotlib
import os
import csv
import matplotlib.pyplot
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
    plt.title(symbol)
    pdata['timestamp'] = pd.to_datetime(pdata['timestamp'], unit='ms')
    pdata.set_index('timestamp', inplace=True)
    pdata["volume"] = pdata["sellVol"]+pdata["buyVol"]

    # 合约持仓
    openInterestHist="sumOpenInterest,sumOpenInterestValue".split(',')
    openInterestHist.append("volume")
    openInterestHist.append("closePrice")

    plt.figure()
    plt.title(symbol)
    pdata[openInterestHist].plot(subplots=True)
    plt.savefig(basepath+symbol+'.png', dpi=300)

    matplotlib.pyplot.close('all')
    # # 大户账户多空比
    plt.figure()
    plt.title(symbol)
    topLongShortAccountRatio="topacclongShortRatio,toplongAccount,topshortAccount".split(',')
    topLongShortAccountRatio.append("closePrice")
    pdata[topLongShortAccountRatio].plot(subplots=True)
    plt.savefig(basepath+symbol+'_topLongShortAccountRatio.png', dpi=300)
    # # 大户持仓量多空比
    plt.figure()
    plt.title(symbol)
    topLongShortPositionRatio="topposlongShortRatio,longPosition,shortPosition".split(',')
    topLongShortPositionRatio.append("closePrice")
    pdata[topLongShortPositionRatio].plot(subplots=True)
    plt.savefig(basepath+symbol+'_topLongShortPositionRatio.png', dpi=300)

    # # 多空持仓人数比
    plt.figure()
    plt.title(symbol)
    globalLongShortAccountRatio="globallongShortRatio,globallongAccount,globalshortAccount".split(',')
    globalLongShortAccountRatio.append("closePrice")

    pdata[globalLongShortAccountRatio].plot(subplots=True)
    plt.savefig(basepath+symbol+'_globalLongShortAccountRatio.png', dpi=300)


if len(sys.argv) > 1:
    symbol = sys.argv[1]
    f = os.path.join('./csvs', symbol+'.csv')
    figure_plot(f, symbol)
    sys.exit(0)
else:
    csvs = os.listdir('./csvs')
    for csv in csvs:
        symbol = csv.split('.')[0]
        f = os.path.join('./csvs', csv)
        data = pd.read_csv(f)
        figure_plot(f, symbol)

