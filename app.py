from flask import Flask, jsonify, send_from_directory
from model import generate_signal
import os

app = Flask(__name__)

latest_signal = {"signal": None, "time": None}

@app.route('/')
def home():
    return "Crypto Signal API is live!"

@app.route('/signal')
def signal():
    global latest_signal
    try:
        latest_signal = generate_signal()
        return jsonify(latest_signal)
    except Exception as e:
        return jsonify({"error": "Signal generation failed", "details": str(e)}), 500

@app.route('/latest-signal')
def latest():
    return jsonify(latest_signal)

# ✅ Serve signals.json publicly
@app.route('/signals.json')
def signals_file():
    return send_from_directory('.', 'signals.json')

# Required by Render to bind to a port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
