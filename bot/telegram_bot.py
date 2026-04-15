import requests
from config import TELEGRAM_TOKEN, CHAT_ID

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if not resp.ok:
            print(f"[Telegram Warning] Non-OK response: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[Telegram Error] {e}")
