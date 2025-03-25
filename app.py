from flask import Flask, jsonify
from model import generate_signal
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Crypto Signal API is live!"

@app.route('/signal')
def signal():
    result = generate_signal()
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's port
    app.run(host='0.0.0.0', port=port)