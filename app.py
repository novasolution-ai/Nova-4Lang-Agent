import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "nova_verify_123")

SYSTEM_PROMPT = """You are Nova 4Lang Agent. Auto-detect user language (Urdu/Hindi/English/Punjabi Roman) and reply in SAME language. Be helpful, friendly. Business: AeroCart."""

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Nova 4Lang Agent is LIVE!"})

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403

    data = request.get_json()
    try:
        # Yahan se Meta AI ka message aayega
        msg = data['entry'][0]['changes'][0]['value'].get('messages', [{}])[0].get('text', {}).get('body', '')
        if msg and client.api_key:
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":msg}]
            )
            print("Reply:", res.choices[0].message.content)
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "ok"}), 200
