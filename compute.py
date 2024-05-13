import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 模拟时间序列数据
pdata = pd.read_csv("./csvs/WLDUSDT.csv")
# pdata['timestamp'] = pd.to_datetime(pdata['timestamp'], unit='ms')
# pdata.set_index('timestamp', inplace=True)
pdata["volume"] = pdata["sellVol"]+pdata["buyVol"]

data = pdata["volume"].values
timestamps = pdata["timestamp"].values


# 设定阈值
threshold = 0.2

# 计算移动平均变化率
def compute_ma_change_rate(data, window_size):
    ma = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
    ma_change_rate = np.diff(ma) / ma[:-1]
    return ma_change_rate

# 监测变化率并触发预警
def monitor_change_rate(data, threshold, window_size, name):
    ma_change_rate = compute_ma_change_rate(data, window_size)
    for i, rate in enumerate(ma_change_rate):
        if abs(rate) > threshold:
            print(f"预警：第{i+window_size}个数据点发生了剧烈变化，变化率为{rate:.2f}")

    dates = [datetime.fromtimestamp(timestamp / 1000).replace(minute=0, second=0) for timestamp in timestamps]
    # 绘制时间序列数据和变化率图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.plot_date(dates, data, 'b-', label='time series data')
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.set_ylabel('value')
    ax1.legend()

    ax2.plot_date(dates[window_size:], ma_change_rate, 'r-', label='average change rate')
    ax2.axhline(y=threshold, color='g', linestyle='--', label='threshold')
    ax2.axhline(y=-threshold, color='g', linestyle='--')
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.set_xlabel('time')
    ax2.set_ylabel('change rate')
    ax2.legend()
    plt.tight_layout()

    plt.savefig("{}.png".format(name), dpi=300)


# 调用监测函数
window_size = 5  # 移动平均窗口大小
monitor_change_rate(data, threshold, window_size, "volume")

monitor_change_rate(pdata["sumOpenInterestValue"].values, threshold, window_size, "sumOpenInterestValue")
