from config import TELEGRAM_TOKEN, CHAT_ID
from ai_model import ai_predict
from telegram_bot import send_telegram
from execution import place_order

print("💀 AJAY AI BOT LIVE")

send_telegram("🚀 BOT STARTED")

# Waiting for TradingView webhook
