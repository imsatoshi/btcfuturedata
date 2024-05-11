import requests
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from git import Repo
os.chdir('/root/btcfuturedata')
filename = 'btc_future.csv'
if not os.path.exists(filename):
    fff = open(filename, 'w', newline='')
    fff.write('timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,topposlongShortRatio,longPosition,shortPosition,globallongShortRatio,globallongAccount,globalshortAccount,basisRate,futuresPrice,basis\n')
    fff.close()


symbol = "BTCUSDT"
period = "5m"
limit = "500"
contract="PERPETUAL"

csvMap = {
    # 合约持仓量
    "openInterestHist": f'https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period={period}&limit={limit}',
    # 大户账户多空比
    "topLongShortAccountRatio": f'https://fapi.binance.com/futures/data/topLongShortAccountRatio?symbol={symbol}&period={period}&limit={limit}',
    # 大户持仓量多空比
    "topLongShortPositionRatio": f'https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol={symbol}&period={period}&limit={limit}',
    # 多空持仓人数比
    "globalLongShortAccountRatio": f'https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period={period}&limit={limit}',
    # 合约主动买卖量 
    "takerBuySellVol": f'https://fapi.binance.com/futures/data/takerBuySellVol?symbol={symbol}&contractType={contract}&period={period}&limit={limit}',
    # 基差
    "basis": f'https://fapi.binance.com/futures/data/basis?pair={symbol}&contractType={contract}&period={period}&limit={limit}'
}

# 合约持仓量
url = f'https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period={period}&limit={limit}'

columns = [
    "openInterestHist",
    "topLongShortAccountRatio", 
    "topLongShortPositionRatio",
    "globalLongShortAccountRatio",
    # "takerBuySellVol",
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
        oi_json = oi_data.json()
        ois.append(oi_json)
    
    for index in range(int(limit)):
        line = []
        timestamp = ois[0][index]['timestamp']
        if timestamp in timestamps:
            print(f"数据已存在，无需写入！")
            continue
        else:
            row = ois[0]
            print("openInterestHist")
            line.extend([timestamp, row[index]['sumOpenInterest'], row[index]['sumOpenInterestValue']])   # 合约持仓
            row = ois[1]
            print("topLongShortAccountRatio")
            line.extend([row[index]['longShortRatio'], row[index]['longAccount'], row[index]['shortAccount']]) # 大户数多空比
            row = ois[2]
            print("topLongShortPositionRatio")
            line.extend([row[index]['longShortRatio'], row[index]['longAccount'], row[index]['shortAccount']]) # 大户持仓多空比
            row = ois[3]
            print("globalLongShortAccountRatio")
            line.extend([row[index]['longShortRatio'], row[index]['longAccount'], row[index]['shortAccount']]) # 多空持仓人数比
            print("basis")
            row = ois[4]
            line.extend([row[index]['basisRate'], row[index]['futuresPrice'], row[index]["basis"]])  # 基差
            print(f"数据 {timestamp} 已成功写入！")

            print(len(line))
            writer.writerow(line)


import matplotlib.pyplot as plt
# visualize the data in the csv file using pandas
pdata = pd.read_csv(filename)
pdata['timestamp'] = pd.to_datetime(pdata['timestamp'], unit='ms')
pdata.set_index('timestamp', inplace=True)

# 合约持仓
openInterestHist="sumOpenInterest,sumOpenInterestValue".split(',')
plt.figure()
pdata[openInterestHist].plot(subplots=True)
plt.savefig('btc_openinteresthist.png', dpi=300)
# 大户账户多空比
plt.figure()
topLongShortAccountRatio="topacclongShortRatio,toplongAccount,topshortAccount".split(',')
pdata[topLongShortAccountRatio].plot(subplots=True)
plt.savefig('btc_topLongShortAccountRatio.png', dpi=300)
# 大户持仓量多空比
plt.figure()
topLongShortPositionRatio="topposlongShortRatio,longPosition,shortPosition".split(',')
pdata[topLongShortPositionRatio].plot(subplots=True)
plt.savefig('btc_topLongShortPositionRatio.png', dpi=300)
# 多空持仓人数比
plt.figure()
globalLongShortAccountRatio="globallongShortRatio,globallongAccount,globalshortAccount".split(',')
pdata[globalLongShortAccountRatio].plot(subplots=True)
plt.savefig('btc_globalLongShortAccountRatio.png', dpi=300)

# 基差
plt.figure()
basis="basisRate,futuresPrice,basis".split(',')
pdata[basis].plot(subplots=True, figsize=(20, 20))
plt.savefig('btc_basis.png', dpi=300)



repo_path = '/root/btcfuturedata'
repo = Repo(repo_path)
repo.git.add(all=True)
repo.git.commit("-m", "auto submit")
repo.git.push()
