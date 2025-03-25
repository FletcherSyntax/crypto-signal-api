import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import requests

def generate_signal():
    # 1. Get recent hourly BTC data
    df = yf.download('BTC-USD', period='7d', interval='1h', auto_adjust=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    # 2. Add technical indicators
    df['sma_20'] = df['Close'].rolling(window=20).mean()

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # 3. Clean data
    df.dropna(inplace=True)
    if df.empty:
        return {"error": "No data after cleaning"}

    # 4. Prepare features
    features = ['Close', 'rsi', 'macd', 'macd_signal', 'sma_20']
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[features])

    X, y = [], []
    lookback = 24  # 24 hours
    for i in range(lookback, len(scaled) - 1):
        X.append(scaled[i - lookback:i])
        y.append(int(df['Close'].iloc[i + 1] > df['Close'].iloc[i]))

    X, y = np.array(X), np.array(y)
    if X.size == 0 or y.size == 0:
        return {"error": "Not enough data to generate signal"}

    # 5. Build & train model
    model = Sequential([
        LSTM(64, input_shape=(X.shape[1], X.shape[2])),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    weights = class_weight.compute_class_weight(class_weight='balanced', classes=np.unique(y), y=y)
    model.fit(X, y, epochs=2, batch_size=32, validation_split=0.2, class_weight=dict(enumerate(weights)), verbose=0)

    # 6. Predict
    preds = model.predict(X, verbose=0)
    df = df.iloc[-preds.shape[0]:]
    df['signal'] = (preds > 0.5).astype(int)
    df['signal_label'] = df['signal'].map({1: 'BUY', 0: 'SELL'})

    latest_signal = df['signal_label'].iloc[-1]
    latest_time = str(df.index[-1])

    # 7. Send webhook
    webhook_url = 'https://webhook.site/2368c67f-23ad-41bc-9442-fdc9e370cc16'  # ← replace this!
    payload = {
        'signal': latest_signal,
        'time': latest_time,
        'symbol': 'BTC-USD',
        'source': 'AI'
    }

    try:
        response = requests.post(webhook_url, json=payload)
        print("✅ Webhook sent:", response.status_code)
    except Exception as e:
        print("❌ Webhook error:", str(e))

    return {
        'time': latest_time,
        'signal': latest_signal
    }
