from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.route("/")
def home():
    return "LIZORD AI Bot is Running!"

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

    reply = response.choices[0].message.content

    return jsonify({
        "reply": reply
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
