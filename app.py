import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Nova 4Lang Agent is LIVE! 🚀 - Working!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    verify_token = os.environ.get("VERIFY_TOKEN", "nova123")
    if request.method == "GET":
        if request.args.get("hub.verify_token") == verify_token:
            return request.args.get("hub.challenge")
        return "Verification failed", 403
    return jsonify({"status": "ok"}), 200

@app.route("/health")
def health():
    return jsonify({"ok": True})
