from flask import Flask, jsonify, send_file, make_response
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

@app.route('/signals.json')
def signals_json():
    try:
        with open("signals.json", "r") as f:
            data = f.read()
        response = make_response(data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except FileNotFoundError:
        return jsonify({"error": "signals.json not found"}), 404
