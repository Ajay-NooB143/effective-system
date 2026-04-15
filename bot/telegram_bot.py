import requests
from config import TELEGRAM_TOKEN, CHAT_ID

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data, timeout=10)
    except requests.RequestException as e:
        print(f"[Telegram] Failed to send message: {e}")
