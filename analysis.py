import pandas as pd
import os
import talib

import matplotlib.pyplot as plt

max_globalaccratio = 0

s1 = ""

max_slope = 0.0
csvs = os.listdir('./csvs')[:10]
for csv in csvs:
    symbol = csv.split('.')[0]
    f = os.path.join('./csvs', csv)
    data = pd.read_csv(f)
    globalacccratio = data["sumOpenInterestValue"]
    data["volume"] = data["sellVol"]+data["buyVol"]
    data["sumOpenInterestValue_1"]=data["sumOpenInterestValue"].apply(lambda x: (x - data["sumOpenInterestValue"].min()) / (data["sumOpenInterestValue"].max() - data["sumOpenInterestValue"].min()))
    data["globallongShortRatio_1"]=data["globallongShortRatio"].apply(lambda x: (x - data["globallongShortRatio"].min()) / (data["globallongShortRatio"].max() - data["globallongShortRatio"].min()))
    data["LINEARREG_SLOPE1"]=talib.LINEARREG_SLOPE(data["sumOpenInterestValue_1"], timeperiod=3)
    data["LINEARREG_SLOPE2"]=talib.LINEARREG_SLOPE(data["globallongShortRatio_1"], timeperiod=3)
    lists="sumOpenInterestValue,globallongShortRatio".split(',')
    lists.append("LINEARREG_SLOPE1")
    lists.append("LINEARREG_SLOPE2")
    lists.append("volume")
    lists.append("closePrice")
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    plt.tight_layout()
    data[lists].plot(subplots=True)
    plt.savefig("./analysis/{}".format(symbol), dpi=300)
