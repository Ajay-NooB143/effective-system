from config import validate_config
from telegram_bot import send_telegram
from webhook import app

if __name__ == "__main__":
    validate_config()

    print("💀 AJAY AI BOT LIVE")
    send_telegram("🚀 BOT STARTED — Waiting for TradingView webhook...")

    app.run(host="0.0.0.0", port=5000)
