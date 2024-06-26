import os
import time
import datetime
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split


import os
import subprocess
import time

def run_mark_script():
    """
    执行 mark.py 脚本
    """
    try:
        # 使用 subprocess 模块执行 mark.py 脚本
        subprocess.run(["python", "mark.py"])
    except Exception as e:
        print("Error occurred while executing mark.py:", e)



start_time = time.time()
symbol = "APEUSDT"
num_epoch = 700
batch_size = 32
sequence_length = 10
modelpath = "./models"
cols = "timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,globallongShortRatio,globallongAccount,globalshortAccount,buy,openPrice,highPrice,lowPrice,closePrice".split(",")

if not os.path.isdir(modelpath):
    os.mkdir(modelpath)

# to time series
def create_sequences(X, y, sequence_length=10):
    X_sequences, y_sequences = [], []
    for i in range(sequence_length, len(X)):
        X_sequences.append(X[i-sequence_length:i])
        y_sequences.append(y[i]) 
    return np.array(X_sequences), np.array(y_sequences)


def train_model(symbol, sequence_length=sequence_length, num_epoch=num_epoch, batch_size=batch_size):
    df = pd.read_csv('traindata/{}.csv'.format(symbol))
    # data preprocessing, delete lines contain NaN
    df.dropna(inplace=True)
    df = df[cols]
    # feature and label
    X = df.drop(columns=['timestamp', 'buy']).values
    y0 = df['buy'].values
    # Convert the labels to categorical (one-hot encoding)
    y = to_categorical(y0, num_classes=3)
    scaler = MinMaxScaler()
    X_seq, y_seq = create_sequences(X, y)
    # zero one
    scaler = MinMaxScaler()
    x_shape = X_seq.shape
    X_normalized_flat = scaler.fit_transform(X_seq.reshape(-1, X_seq.shape[-1]))
    X_normalized = X_normalized_flat.reshape((-1, x_shape[1], x_shape[2]))
    # train test split
    X_train, X_test, y_train, y_test = train_test_split(X_normalized, y_seq, test_size=0.2, random_state=42)
    # LSTM
    model = Sequential([
        LSTM(units=256, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        LSTM(units=256, return_sequences=True),
        Dropout(0.2),
        LSTM(units=256),
        Dropout(0.2),
        Dense(units=3, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=num_epoch, batch_size=batch_size, validation_data=(X_test, y_test))
    test_loss, test_acc = model.evaluate(X_test, y_test)
    print('Test loss:\t', test_loss, '\n', 'Test accuracy:', test_acc)

    # 获取当前时间
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 保存模型，带有时间戳
    model.save(f'models/{symbol}_{current_time}.h5')
    print("Consuming Time: {}s".format(time.time() - start_time))

    # save scaler
    df.to_csv("scaler.csv")


if __name__ == "__main__":
    run_mark_script()
    train_model(symbol)


