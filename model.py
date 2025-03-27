import yfinance as yf
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os

def generate_signal():
    # 1. Download BTC-USD hourly data
    df = yf.download('BTC-USD', interval='60m', period='14d', auto_adjust=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    print("\n📊 Rows after download:", len(df))

    # 2. Indicators
    df['sma_50'] = df['Close'].rolling(window=50).mean()

    delta = df['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain.ravel()).rolling(window=14).mean()
    avg_loss = pd.Series(loss.ravel()).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    print("\n🔍 NaN count per column before dropna():")
    print(df.isna().sum())

    df.dropna(inplace=True)
    print("✅ Rows after dropna():", len(df))

    # 3. Prepare features
    features = ['Close', 'rsi', 'macd', 'macd_signal', 'sma_50']
    if len(df) < 50:
        raise ValueError(f"Not enough data after preprocessing. Needed at least 50, got {df.shape[0]}")

    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(df[features])

    # 4. Create sequences
    X, y = [], []
    lookback = 48
    for i in range(lookback, len(scaled_features) - 1):
        X.append(scaled_features[i - lookback:i])
        y.append(int(df['Close'].iloc[i + 1] > df['Close'].iloc[i]))

    X, y = np.array(X), np.array(y)

    if len(X) == 0:
        raise ValueError("Not enough data for model training.")

    # 5. Train model
    model = Sequential([
        LSTM(64, input_shape=(X.shape[1], X.shape[2])),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    # 6. Predict
    preds = model.predict(X, verbose=0)
    df = df.iloc[-preds.shape[0]:]
    df['signal'] = (preds > 0.5).astype(int)
    df['signal_label'] = df['signal'].map({1: 'BUY', 0: 'SELL'})

    latest_signal = df['signal_label'].iloc[-1]
    latest_time = str(df.index[-1])

    # 7. Export to signals.json
    signal_times = [int(ts.timestamp()) for ts in df.index[-200:]]
    signal_values = df['signal'].values[-200:].astype(int).tolist()

    signal_data = {
        "times": signal_times,
        "signals": signal_values
    }

    with open("signals.json", "w") as f:
        json.dump(signal_data, f)

    print("✅ Exported latest signals to signals.json")

    return {
        'time': latest_time,
        'signal': latest_signal
    }

if __name__ == "__main__":
    generate_signal()
