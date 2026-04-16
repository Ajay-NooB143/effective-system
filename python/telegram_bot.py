"""Telegram notification helper."""

import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def send_message(text: str) -> None:
    """Send a plain-text message to the configured Telegram chat.

    Does nothing (logs a warning) when credentials are missing so the rest
    of the pipeline can keep running in a development / test environment.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[Telegram] (no credentials) {text}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as exc:  # pragma: no cover
        print(f"[Telegram] failed to send message: {exc}")
