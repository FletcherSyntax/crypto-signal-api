import requests

url = 'https://crypto-signal-api.onrender.com/signal'

try:
    print("⏰ Triggering hourly signal...")
    response = requests.get(url)
    print("✅ Response:", response.json())
except Exception as e:
    print("❌ Error:", e)