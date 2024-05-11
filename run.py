import requests
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from git import Repo

os.chdir('/root/btcfuturedata')
symbol = "BTCUSDT"
period = "5m"
limit = "100"

url = f'https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period={period}&limit={limit}'

oi_data = requests.get(url)
oi_json = oi_data.json()

filename = 'btc_openinteresthist.csv'
if not os.path.exists(filename):
    fff = open(filename, 'w', newline='')
    fff.write('timestamp,sumOpenInterest,sumOpenInterestValue\n')
    fff.close()

pdata = pd.read_csv(filename)
timestamps = pdata['timestamp'].tolist()

with open(filename, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    n = 0

    for d in oi_json:
        if d['timestamp'] in timestamps:
            continue
        else:
            writer.writerow([d['timestamp'], d['sumOpenInterest'], d['sumOpenInterestValue']])
            print(f"数据 {d['timestamp']} 已成功写入！")
            n += 1

    if n > 0:
        print(f"数据已成功写入到 {filename} 文件中！")
    else:
        print(f"数据已存在，无需写入！")


# visualize the data in the csv file using pandas
pdata = pd.read_csv(filename)
pdata['timestamp'] = pd.to_datetime(pdata['timestamp'], unit='ms')
pdata.set_index('timestamp', inplace=True)
pdata.plot(subplots=True, figsize=(10, 10))
plt.savefig('btc_openinteresthist.png')


repo_path = '/root/btcfuturedata'
repo = Repo(repo_path)
repo.git.add(all=True)
repo.git.commit("-m", "auto submit")
repo.git.push()
