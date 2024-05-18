import os
import sys
import time
import requests
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from datetime import datetime
import pbinance
start_time = time.time()
symbol = "APEUSDT"
period = "5m"
limit = 10

model_folder = 'models'  # 模型文件夹路径

# 获取模型文件夹下所有模型文件
model_files = [f for f in os.listdir(model_folder) if f.endswith('.h5')]
latest_model_file = ""
if model_files:  # 检查是否有模型文件
    # 提取时间戳并排序
    timestamps = [int(f.split('_')[-1].split('.')[0]) for f in model_files]
    max_timestamp_index = timestamps.index(max(timestamps))
    latest_model_file = model_files[max_timestamp_index]
    
    # 打印最新模型文件名
    print("最新的模型文件:", latest_model_file)
else:
    print("模型文件夹中没有模型文件。")
    sys.exit()

model_path = "{}/{}".format(model_folder, latest_model_file)
print(model_path)
# 读取数据
df = pd.read_csv('traindata/{}.csv'.format(symbol))

# 数据预处理, 删除包含 NaN 值的行
df.dropna(inplace=True)

# 特征工程：将时间序列转换为序列数据
def create_sequences(X, y, sequence_length=10):
    X_sequences, y_sequences = [], []
    for i in range(sequence_length, len(X)):
        X_sequences.append(X[i-sequence_length:i])
        y_sequences.append(y[i])  # 对应的标签就是当前行的y值
    return np.array(X_sequences), np.array(y_sequences)


def get_current_timestamp():
    # 获取当前时间
    current_time = datetime.now()

    # 计算当前时间距离上一个能被 5 整除的分钟数
    minutes = current_time.minute
    nearest_five_minute = (minutes // 5) * 5

    # 获取最近的五分钟的起始时间
    nearest_time = current_time.replace(minute=nearest_five_minute, second=0, microsecond=0)

    # 将最近的五分钟的起始时间转换为时间戳
    nearest_timestamp = int(nearest_time.timestamp())*1000

    # 输出最近的五分钟的时间戳

    return nearest_timestamp


cols = "timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,globallongShortRatio,globallongAccount,globalshortAccount,buy,openPrice,highPrice,lowPrice,closePrice".split(",")
df = df[cols]

# 将数据划分为特征和标签
X = df.drop(columns=['timestamp', 'buy']).values
y = df['buy'].values
scaler = MinMaxScaler()
X_seq, y_seq = create_sequences(X, y)

# 归一化处理
scaler = MinMaxScaler()
x_shape = X_seq.shape
X_normalized_flat = scaler.fit_transform(X_seq.reshape(-1, X_seq.shape[-1]))
X_normalized = X_normalized_flat.reshape((-1, x_shape[1], x_shape[2]))


# 根据 pbinance 获取数据
binance = pbinance.Binance("", "")
newdata = pd.DataFrame(columns=cols)
sumOpenInterests = []
sumOpenInterestValues = []
topacclongShortRatios = []
toplongAccount = []
topshortAccounts = []
globallongShortRatios = []
globallongAccounts = []
globalshortAccounts = []
openPrices = []
highPrices = []
lowPrices = []
closePrices = []

while 1:
    openInterestHist = binance.um.market.get_openInterestHist(symbol=symbol, period=period, limit=limit)["data"]
    topLongShortAccountRatio = binance.um.market.get_topLongShortAccountRatio(symbol=symbol, period=period, limit=limit)["data"]
    topLongShortPositionRatio = binance.um.market.get_topLongShortPositionRatio(symbol=symbol, period=period, limit=limit)["data"]
    globalLongShortAccountRatio = binance.um.market.get_globalLongShortAccountRatio(symbol=symbol, period=period, limit=limit)["data"]
    # takerlongshortRatio = binance.um.market.get_takerlongshortRatio(symbol=symbol, period=period,limit=limit)["data"]
    prices = binance.um.market.get_markPriceKlines(symbol=symbol, interval=period, limit=limit)["data"]
    last_openInterestHist = openInterestHist[-1]
    last_toplongshortAccRatio = topLongShortAccountRatio[-1]
    last_toplongposRatio = topLongShortPositionRatio[-1]
    last_globalongshortAccratio = globalLongShortAccountRatio[-1]
    last_price = prices[-1]


    if last_openInterestHist["timestamp"] == last_toplongposRatio["timestamp"] == last_toplongshortAccRatio["timestamp"] == last_globalongshortAccratio["timestamp"] == last_price[0]:
        for oi, ta, tp, ga, ps in zip(openInterestHist, topLongShortAccountRatio, topLongShortPositionRatio, globalLongShortAccountRatio, prices):
            # print(oi["timestamp"], ta["timestamp"], tp["timestamp"], ga["timestamp"], ps[0])
            sumOpenInterests.append(float(oi["sumOpenInterest"]))
            sumOpenInterestValues.append(float(oi["sumOpenInterestValue"]))
            topacclongShortRatios.append(float(ta["longShortRatio"]))
            toplongAccount.append(float(ta["longAccount"]))
            topshortAccounts.append(float(ta["shortAccount"]))
            globallongShortRatios.append(float(ga["longShortRatio"]))
            globallongAccounts.append(float(ga["longAccount"]))
            globalshortAccounts.append(float(ga["shortAccount"]))
            openPrices.append(float(ps[1]))
            highPrices.append(float(ps[2]))
            lowPrices.append(float(ps[3]))
            closePrices.append(float(ps[4]))
        break
    else:
        print("wait...")
        print("wait...", last_openInterestHist["timestamp"])
        time.sleep(0.1)
    
vectors = np.column_stack((sumOpenInterests,sumOpenInterestValues,topacclongShortRatios, toplongAccount, topshortAccounts, globallongShortRatios, globallongAccounts, globalshortAccounts,openPrices, highPrices, lowPrices, closePrices))
vshape = vectors.shape
X_flat = scaler.fit_transform(vectors.reshape(-1, vectors.shape[-1]))
X_ = X_flat.reshape((1, vshape[0], vshape[1]))

# 加载模型
model = load_model(model_path)

# 对新数据进行预测
predicted_labels = model.predict(X_)
# 输出预测结果
print(predicted_labels)

label = ["buy", "nothing", "sell"][predicted_labels.argmax()]
title = label
message = ""
message += ",".join([str(_) for _ in predicted_labels[0].tolist()])
message += ",".join([str(_) for _ in sumOpenInterests])+"\n"
message += ",".join([str(_) for _ in sumOpenInterestValues])+"\n"
message += ",".join([str(_) for _ in topacclongShortRatios])+"\n"
message += ",".join([str(_) for _ in toplongAccount])+"\n"
message += ",".join([str(_) for _ in topshortAccounts])+"\n"
message += ",".join([str(_) for _ in globallongShortRatios])+"\n"
message += ",".join([str(_) for _ in globallongAccounts])+"\n"
message += ",".join([str(_) for _ in globalshortAccounts])+"\n"
message += ",".join([str(_) for _ in closePrices])+"\n"
requests.post("https://api.day.app/Rn4sQCRDQr3TYNaBuKoGZe/{}/{}".format(title, message))

print(sumOpenInterests)
print(sumOpenInterestValues)
print(topacclongShortRatios)
print(toplongAccount)
print(topshortAccounts)
print(globallongShortRatios)
print(globallongAccounts)
print(globalshortAccounts)
print(openPrices[-1])
print(highPrices[-1])
print(lowPrices[-1])
print(closePrices[-1])


end_time = time.time()

print("prediction consume {} s".format(end_time - start_time))

print(last_openInterestHist["timestamp"])

