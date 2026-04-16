import os
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MODE = os.getenv("MODE", "SAFE")  # SAFE = simulation, LIVE = real orders

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # Set to validate TradingView requests

ORDER_QTY_STR = os.getenv("ORDER_QTY", "0.001")
try:
    ORDER_QTY = float(ORDER_QTY_STR)
except ValueError:
    raise EnvironmentError(
        f"Invalid value for ORDER_QTY: '{ORDER_QTY_STR}'. Must be a positive number (e.g. 0.001)."
    )


def validate_config():
    """Raise EnvironmentError if any required variables are missing."""
    _REQUIRED = {
        "BINANCE_API_KEY": BINANCE_API_KEY,
        "BINANCE_SECRET": BINANCE_SECRET,
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "CHAT_ID": CHAT_ID,
    }
    _missing = [k for k, v in _REQUIRED.items() if not v]
    if _missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(_missing)}. "
            "Copy .env.example to .env and fill in your values."
        )
