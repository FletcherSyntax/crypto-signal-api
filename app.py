from flask import Flask, jsonify, send_from_directory
import os
from model import generate_signal

app = Flask(__name__)

latest_signal = {"signal": None, "time": None}

@app.route('/')
def home():
    return "Crypto Signal API is live!"

@app.route('/signal')
def signal():
    global latest_signal
    latest_signal = generate_signal()
    return jsonify(latest_signal)

@app.route('/latest-signal')
def latest():
    return jsonify(latest_signal)

@app.route('/signals.json')
def get_signal_json():
    return send_from_directory(os.getcwd(), 'signals.json')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

