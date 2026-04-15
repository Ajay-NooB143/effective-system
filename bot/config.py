import os
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "YOUR_API_KEY")
BINANCE_SECRET  = os.getenv("BINANCE_SECRET", "YOUR_SECRET")

TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
CHAT_ID         = os.getenv("CHAT_ID", "YOUR_CHAT_ID")

MODE = os.getenv("MODE", "SAFE")   # SAFE / LIVE
