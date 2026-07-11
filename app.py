import os
import re
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

USERNAME_RE = re.compile(r"^[A-Za-z0-9._]{1,30}$")


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=15,
    )


def check_username(username):
    username = username.strip().lstrip("@")

    if not USERNAME_RE.fullmatch(username):
        return f"⚠️ INVALID\n\n@{username}\nFormat username nggak valid."

    url = f"https://www.instagram.com/{username}/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 10) "
            "AppleWebKit/537.36 Chrome/131.0 Mobile Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True,
        )

        if response.status_code == 404:
            return (
                f"👀 NOT FOUND\n\n"
                f"@{username}\n\n"
                f"Belum tentu claimable."
            )

        if response.status_code == 200:
            page = response.text.lower()

            markers = [
                '"username"',
                '"profilepage_',
                'og:description',
            ]

            if any(marker in page for marker in markers):
                return f"❌ TAKEN\n\n@{username}"

            return (
                f"⚠️ UNKNOWN\n\n"
                f"@{username}\n\n"
                f"Instagram ngasih response ambigu."
            )

        if response.status_code == 429:
            return f"⏳ RATE LIMITED\n\n@{username}"

        return (
            f"⚠️ UNKNOWN\n\n"
            f"@{username}\n"
            f"HTTP {response.status_code}"
        )

    except requests.RequestException as e:
        return (
            f"⚠️ ERROR\n\n"
            f"{type(e).__name__}"
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
            "Nevergoat IG Checker\n\n"
            "Kirim username Instagram yang mau dicek."
        )

    elif text.startswith("/check "):
        username = text.split(maxsplit=1)[1]
        send_message(chat_id, check_username(username))

    elif text.startswith("/"):
        send_message(chat_id, "Command nggak dikenal.")

    else:
        send_message(chat_id, check_username(text))

    return "OK", 200
