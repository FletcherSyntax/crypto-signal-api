from flask import Flask, jsonify, send_file
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
def serve_json():
    if os.path.exists("signals.json"):
        return send_file("signals.json", mimetype="application/json")
    else:
        return jsonify({"error": "signals.json not found"}), 404

# 🔧 This is what tells Render how to run your Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
