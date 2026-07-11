import os
import requests

from flask import Flask, request
from instagrapi import Client
from instagrapi.exceptions import UserNotFound

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

cl = Client()


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=15
    )


def check_username(username):
    username = username.strip().lstrip("@").lower()

    if not username:
        return "Kirim username dulu jir."

    try:
        user = cl.user_info_by_username(username)

        return (
            f"❌ TAKEN\n\n"
            f"@{user.username}\n"
            f"Name: {user.full_name or '-'}"
        )

    except UserNotFound:
        return (
            f"👀 NOT FOUND\n\n"
            f"@{username}\n\n"
            f"Belum tentu claimable. Ini cuma hasil lookup."
        )

    except Exception as e:
        return (
            f"⚠️ ERROR\n\n"
            f"{type(e).__name__}: {str(e)[:300]}"
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
    text = message.get("text", "").strip()

    if text == "/start":
        send_message(
            chat_id,
            "Nevergoat IG Checker\n\nKirim username IG yang mau dicek."
        )

    elif text.startswith("/"):
        send_message(chat_id, "Command ga dikenal jir.")

    else:
        send_message(chat_id, check_username(text))

    return "OK", 200
