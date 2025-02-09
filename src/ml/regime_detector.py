import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler

class RegimeDetector:
    def __init__(self, lookback_window=30, hidden_units=50, epochs=10, batch_size=32):
        self.lookback_window = lookback_window
        self.hidden_units = hidden_units
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def prepare_data(self, series: pd.Series):
        data = series.values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(data)
        X, y = [], []
        for i in range(self.lookback_window, len(scaled_data)):
            X.append(scaled_data[i - self.lookback_window:i, 0])
            y.append(scaled_data[i, 0])
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        return X, y

    def build_model(self, input_shape):
        model = Sequential([
            Input(shape=input_shape),
            LSTM(units=self.hidden_units, return_sequences=True),
            Dropout(0.2),
            LSTM(units=self.hidden_units),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        self.model = model

    def train(self, series: pd.Series):
        X, y = self.prepare_data(series)
        self.build_model((X.shape[1], 1))
        self.model.fit(X, y, epochs=self.epochs, batch_size=self.batch_size, verbose=1)

    def predict(self, series: pd.Series):
        X, _ = self.prepare_data(series)
        predictions = self.model.predict(X)
        predictions = self.scaler.inverse_transform(predictions)
        return predictions