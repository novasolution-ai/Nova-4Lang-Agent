
import os
from flask import Flask, request
import requests
from groq import Groq

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "nova_verify_123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SYSTEM_PROMPT = """
You are Nova, a helpful assistant for Nova Solutions.
You MUST detect user's language from last message and reply in SAME language.
Supported: Urdu (Roman Urdu), English, Punjabi (Roman), Saraiki.
- If user writes Urdu Roman like 'salam kya hal hai' -> reply in Urdu Roman
- If English -> reply in English
- If Punjabi -> reply in Punjabi Roman
- If Saraiki -> reply in Saraiki
Keep tone friendly and short.
Company: Nova Solutions provides WhatsApp automation, websites, digital marketing.
"""

def send_whatsapp(to, text):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("Missing tokens")
        return
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    r = requests.post(url, headers=headers, json=data)
    print("Send status:", r.status_code, r.text)

def get_ai_reply(user_msg):
    if not client:
        return "Salam! Main Nova hun. Aap kaise madad chahte hain?"
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("Groq error:", e)
        return "Thora masla ho raha hai, dobara try karen."

@app.route("/")
def home():
    return "Nova 4Lang Agent is Live - /webhook ready", 200

@app.route("/healthz")
def health():
    return "ok", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403
    if request.method == "POST":
        data = request.get_json()
        try:
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            if "messages" in value:
                msg = value["messages"][0]
                from_num = msg["from"]
                text = msg.get("text", {}).get("body", "")
                if text:
                    reply = get_ai_reply(text)
                    send_whatsapp(from_num, reply)
        except Exception as e:
            print("Webhook error:", e)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
