import pandas as pd
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

from sklearn.model_selection import train_test_split

# 读取数据
df = pd.read_csv('traindata/1000BONKUSDT.csv')

# 数据预处理
# 删除包含 NaN 值的行
df.dropna(inplace=True)


# 特征工程：将时间序列转换为序列数据
def create_sequences(X, y, sequence_length=10):
    X_sequences, y_sequences = [], []
    for i in range(sequence_length, len(X)):
        X_sequences.append(X[i-sequence_length:i])
        y_sequences.append(y[i])  # 对应的标签就是当前行的y值
    return np.array(X_sequences), np.array(y_sequences)


# cols = "timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,topposlongShortRatio,longPosition,shortPosition,globallongShortRatio,globallongAccount,globalshortAccount,buySellRatio,sellVol,buyVol,openPrice,highPrice,lowPrice,closePrice".split(",")
cols = "timestamp,sumOpenInterest,sumOpenInterestValue,longPosition,shortPosition,globallongShortRatio,globallongAccount,globalshortAccount,buySellRatio,sellVol,buyVol,buy".split(",")
df = df[cols]

# 将数据划分为特征和标签
X = df.drop(columns=['timestamp', 'buy']).values
y = df['buy'].values
scaler = MinMaxScaler()
np.save('scaler_params.npy', [scaler.min_, scaler.scale_])

# 创建序列数据
X_seq, y_seq = create_sequences(X, y)

# 归一化处理
scaler = MinMaxScaler()
x_shape = X_seq.shape
X_normalized_flat = scaler.fit_transform(X_seq.reshape(-1, X_seq.shape[-1]))
X_normalized = X_normalized_flat.reshape((-1, x_shape[1], x_shape[2]))

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_normalized, y_seq, test_size=0.2, random_state=42)



# 构建深层循环神经网络模型
model = Sequential([
    LSTM(units=128, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.2),
    LSTM(units=128, return_sequences=True),
    Dropout(0.2),
    LSTM(units=128),
    Dropout(0.2),
    Dense(units=1, activation='sigmoid')
])


# 编译模型
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 训练模型
model.fit(X_train, y_train, epochs=1000, batch_size=32, validation_data=(X_test, y_test))

# 在测试集上评估模型
test_loss, test_acc = model.evaluate(X_test, y_test)
print('Test accuracy:', test_acc)
model.save('models/1000BONKUSDT.h5')

