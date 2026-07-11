import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=15
    )


@app.route("/")
def home():
    return "Bot is alive", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}

    message = update.get("message")
    if not message:
        return "OK", 200

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        send_message(chat_id, "Nevergoat IG Checker is alive.")
    else:
        send_message(chat_id, f"Lu ngirim: {text}")

    return "OK", 200
