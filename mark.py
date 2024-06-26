import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
cols = "timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,topposlongShortRatio,longPosition,shortPosition,globallongShortRatio,globallongAccount,globalshortAccount,buySellRatio,sellVol,buyVol,openPrice,highPrice,lowPrice,closePrice,buy".split(",")


# git pull
def git_pull():
    try:
        subprocess.run(["git", "pull"])
    except Exception as e:
        print("Error occurred while executing git pull:", e)


def visulalize(datapath):
    # 可视化
    df = pd.read_csv(datapath)
    plt.figure(figsize=(10, 6))
    df['tt'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df.plot(x='tt', y='closePrice', label='Close Price', color='blue', ax=plt.gca())
    plt.scatter(df[df['buy'] == 1]['tt'], df[df['buy'] == 1]['closePrice'], color='green', label='Buy Signal')
    plt.scatter(df[df['buy'] == -1]['tt'], df[df['buy'] == -1]['closePrice'], color='red', label='Sell Signal')
    plt.xlabel('Timestamp')
    plt.ylabel('Close Price')
    plt.title('Close Price vs Timestamp with Buy/Sell Signal')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("analysis/{}.png".format(symbol), dpi=300)


def mark_data(symbol, trainpath="./traindata", n=30, p=0.011, p2=0.03):
    if not os.path.isdir(trainpath):
        os.mkdir(trainpath)
    f = './csvs/{}.csv'.format(symbol)
    train_f = './{}/{}.csv'.format(trainpath, symbol)
    df = pd.read_csv(f)
    # 将时间戳列转换为 datetime 类型
    df['closePrice'] = df['closePrice'].astype(float)
    df['buy'] = 0
    # 初始化标签列
    # 计算未来十个单位时间内的最大涨幅，并找到第一个超过2%的点
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
    df = df[cols]
    num_buy = df[df['buy'] == 1].shape[0]
    num_sell = df[df['buy'] == -1].shape[0]
    # save to train path
    df.to_csv(train_f)
    return num_buy, num_sell, df.shape[0]


if __name__ == "__main__":
    git_pull()
    csvs = os.listdir('./csvs')
    for csv in csvs:
        symbol = csv.split(".")[0]
        buy, sell, total = mark_data(symbol)
        print(symbol, buy, sell, total, 1.0 * buy / total, 1.0 * sell / total)
        # visulalize("./traindata/{}.csv".format(symbol))
