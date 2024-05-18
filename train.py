import os
import pandas as pd
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.utils import to_categorical

from sklearn.model_selection import train_test_split
modelpath = "./models"
trainpath = "./traindata"

symbol = "UMAUSDT"

if not os.path.isdir(modelpath):
    os.mkdir(modelpath)



# load data
df = pd.read_csv('{}/{}.csv'.format(trainpath, symbol))

# data preprocessing, delete lines contain NaN
df.dropna(inplace=True)


# to time series
def create_sequences(X, y, sequence_length=10):
    X_sequences, y_sequences = [], []
    for i in range(sequence_length, len(X)):
        X_sequences.append(X[i-sequence_length:i])
        y_sequences.append(y[i]) 
    return np.array(X_sequences), np.array(y_sequences)


cols = "timestamp,sumOpenInterest,sumOpenInterestValue,topacclongShortRatio,toplongAccount,topshortAccount,globallongShortRatio,globallongAccount,globalshortAccount,buy,openPrice,highPrice,lowPrice,closePrice".split(",")

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

model.fit(X_train, y_train, epochs=1000, batch_size=32, validation_data=(X_test, y_test))

test_loss, test_acc = model.evaluate(X_test, y_test)
print('Test accuracy:', test_acc)
model.save('{}/{}.h5'.format(modelpath, symbol))



