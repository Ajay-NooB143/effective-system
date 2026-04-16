from config import MODE, TELEGRAM_TOKEN, CHAT_ID, BINANCE_API_KEY, BINANCE_SECRET, validate_config
from telegram_bot import send_telegram
from webhook import app

validate_config()

print("💀 AJAY AI BOT LIVE")
send_telegram("🚀 BOT STARTED — Waiting for TradingView webhook...")

app.run(host="0.0.0.0", port=5000)
