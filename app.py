from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
WHATSAPP_TOKEN = os.environ["WHATSAPP_TOKEN"]
PHONE_NUMBER_ID = os.environ["PHONE_NUMBER_ID"]


@app.route("/")
def home():
    return "LIZORD AI Bot is Running!"


# WhatsApp Webhook Verification
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403


def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    r = requests.post(url, headers=headers, json=payload)
    print(r.status_code, r.text)


# WhatsApp Incoming Messages
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()
    print(data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" in value:

            sender = value["messages"][0]["from"]
            user_message = value["messages"][0]["text"]["body"]

            response = client.responses.create(
                model="gpt-5.5",
                input=[
                    {
                        "role": "system",
                        "content": "You are LIZORD AI Assistant. Reply in Hindi unless the user requests another language."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            reply = response.output_text

            send_whatsapp_message(sender, reply)

    except Exception as e:
        print("ERROR:", e)

    return "EVENT_RECEIVED", 200


# Test API
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data.get("message", "")

    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {
                "role": "system",
                "content": "You are LIZORD AI Assistant."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return jsonify({
        "reply": response.output_text
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )
