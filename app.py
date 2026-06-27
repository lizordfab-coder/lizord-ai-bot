from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")


@app.route("/")
def home():
    return "LIZORD AI Bot is Running!"


# Meta Webhook Verification
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403


# WhatsApp Incoming Messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(data)
    return "EVENT_RECEIVED", 200


# AI Chat API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    message = data.get("message", "")

    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
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
        "reply": response.choices[0].message.content
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )
