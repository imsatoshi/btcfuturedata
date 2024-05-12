import ccxt
import requests
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from git import Repo
os.chdir('/root/btcfuturedata')

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

def write_to_csv(symbol):
    # symbol = "BTCUSDT"
    period = "5m"
    limit = "100"
    contract="PERPETUAL"
    filename = './csvs/{}.csv'.format(symbol)
    if not os.path.exists(filename):
        fff = open(filename, 'w', newline='')
        fff.write('timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,topposlongShortRatio,longPosition,shortPosition,globallongShortRatio,globallongAccount,globalshortAccount,basisRate,futuresPrice,basis\n')
        fff.close()

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
        "basis": f'https://fapi.binance.com/futures/data/basis?pair={symbol}&contractType={contract}&period={period}&limit={limit}'
    }

    columns = [
        "openInterestHist",
        "topLongShortAccountRatio", 
        "topLongShortPositionRatio",
        "globalLongShortAccountRatio",
        "basis"
    ]

    pdata = pd.read_csv(filename)
    timestamps = pdata['timestamp'].tolist()

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        ois = []
        
        for col in columns:
            url = csvMap[col]
            oi_data = requests.get(url)
            if oi_data.status_code != 200:
                return oi_data.status_code
            oi_json = oi_data.json()
            ois.append(oi_json)
        
        for index in range(int(limit)):
            line = []
            timestamp = ois[0][index]['timestamp']
            if timestamp in timestamps:
                continue
            else:
                row = ois[0]
                line.extend([timestamp, row[index]['sumOpenInterest'], row[index]['sumOpenInterestValue']])   # 合约持仓
                row = ois[1]
                line.extend([row[index]['longShortRatio'], row[index]['longAccount'], row[index]['shortAccount']]) # 大户数多空比
                row = ois[2]
                line.extend([row[index]['longShortRatio'], row[index]['longAccount'], row[index]['shortAccount']]) # 大户持仓多空比
                row = ois[3]
                line.extend([row[index]['longShortRatio'], row[index]['longAccount'], row[index]['shortAccount']]) # 多空持仓人数比
                row = ois[4]
                line.extend([row[index]['basisRate'], row[index]['futuresPrice'], row[index]["basis"]])  # 基差
                writer.writerow(line)

def figure_plot(filename, symbol, basepath="./figures/"):
    # visualize the data in the csv file using pandas
    pdata = pd.read_csv(filename)
    pdata['timestamp'] = pd.to_datetime(pdata['timestamp'], unit='ms')
    pdata.set_index('timestamp', inplace=True)

    # 合约持仓
    openInterestHist="sumOpenInterest,sumOpenInterestValue,futuresPrice".split(',')
    plt.figure()
    pdata[openInterestHist].plot(subplots=True)
    plt.savefig(basepath+symbol+'_openinteresthist.png', dpi=300)
    # 大户账户多空比
    plt.figure()
    topLongShortAccountRatio="topacclongShortRatio,toplongAccount,topshortAccount".split(',')
    pdata[topLongShortAccountRatio].plot(subplots=True)
    plt.savefig(basepath+symbol+'_topLongShortAccountRatio.png', dpi=300)
    # 大户持仓量多空比
    plt.figure()
    topLongShortPositionRatio="topposlongShortRatio,longPosition,shortPosition".split(',')
    pdata[topLongShortPositionRatio].plot(subplots=True)
    plt.savefig(basepath+symbol+'_topLongShortPositionRatio.png', dpi=300)
    # 多空持仓人数比
    plt.figure()
    globalLongShortAccountRatio="globallongShortRatio,globallongAccount,globalshortAccount".split(',')
    pdata[globalLongShortAccountRatio].plot(subplots=True)
    plt.savefig(basepath+symbol+'_globalLongShortAccountRatio.png', dpi=300)

    # 基差
    plt.figure()
    basis="basisRate,futuresPrice,basis".split(',')
    pdata[basis].plot(subplots=True, figsize=(20, 20))
    plt.savefig(basepath+symbol+'_basis.png', dpi=300)


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
        print(m)

        statuscode = write_to_csv(symbol)

# plot btc future data
for s in ['BTC', "ETH", "BNB"]:
    filename = "./csvs/{}USDT.csv".format(s)
    figure_plot(filename, s)


repo_path = '/root/btcfuturedata'
repo = Repo(repo_path)
repo.git.add(all=True)
repo.git.commit("-m", "auto submit!!!")
repo.git.push()
