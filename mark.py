import os
import subprocess

# 执行 git pull 命令
def git_pull():
    try:
        subprocess.run(["git", "pull"])
    except Exception as e:
        print("Error occurred while executing git pull:", e)

# 在 mark.py 运行前执行 git pull
git_pull()


import pandas as pd
import matplotlib.pyplot as plt

n = 30
p = 0.01
p2 = 0.03
trainpath = "./traindata"

if not os.path.isdir(trainpath):
    os.mkdir(trainpath)

csvs = os.listdir('./csvs')
# num_buy = 0
# all_line = 0

max_buy_sell = 0
max_symbol = ""

for csv in csvs:
    symbol = csv.split('.')[0]
    f = os.path.join('./csvs', csv)
    train_f = os.path.join(trainpath, csv)
    df = pd.read_csv(f)
    # 将时间戳列转换为 datetime 类型
    # df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['closePrice'] = df['closePrice'].astype(float)
    df['buy'] = 0
    # 初始化标签列

    for i in range(len(df) - n):
        future_max_price = df['closePrice'].iloc[i:i+n].max()
        future_min_price = df['closePrice'].iloc[i:i+n].min()

        current_price = df['closePrice'].iloc[i]
        # 1 means buy; -1 means sell; 0 means nothing
        if future_max_price > current_price * (1+p) and future_min_price > current_price * (1 - p2):
            df.loc[i, 'buy'] = 1
        if future_min_price < current_price * (1-p) and future_max_price < current_price * (1 + p2):
            df.loc[i, 'buy'] = -1
        

    df.dropna(inplace=True)
    cols = "timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,topposlongShortRatio,longPosition,shortPosition,globallongShortRatio,globallongAccount,globalshortAccount,buySellRatio,sellVol,buyVol,openPrice,highPrice,lowPrice,closePrice,buy".split(",")

    df = df[cols]
    num_buy = df[df['buy'] == 1].shape[0]
    num_sell = df[df['buy'] == -1].shape[0]
    # df.shape =
    if max_buy_sell < 1.0*(num_buy + num_sell) / df.shape[0]:
        max_buy_sell = 1.0 * (num_buy+num_sell) / df.shape[0]
        max_symbol = symbol
        print(symbol, max_buy_sell, df.shape[0])

    df.to_csv(train_f)

    # plt.figure(figsize=(10, 6))
    # df['tt'] = pd.to_datetime(df['timestamp'], unit='ms')
    # df.set_index('timestamp', inplace=True)

    # df.plot(x='tt', y='closePrice', label='Close Price', color='blue', ax=plt.gca())
    # plt.scatter(df[df['buy'] == 1]['tt'], df[df['buy'] == 1]['closePrice'], color='green', label='Buy Signal')
    # plt.scatter(df[df['buy'] == -1]['tt'], df[df['buy'] == -1]['closePrice'], color='red', label='Sell Signal')


    # plt.xlabel('Timestamp')
    # plt.ylabel('Close Price')
    # plt.title('Close Price vs Timestamp with Buy/Sell Signal')
    # plt.legend()
    # plt.grid(True)
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.savefig("analysis/{}.png".format(symbol), dpi=300)

print("Max:\t", max_symbol, max_buy_sell)



