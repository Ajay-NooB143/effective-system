from config import BINANCE_API_KEY, BINANCE_SECRET, MODE, TELEGRAM_TOKEN, CHAT_ID
from binance.client import Client
from binance.exceptions import BinanceAPIException
from telegram_bot import send_telegram

client = Client(BINANCE_API_KEY, BINANCE_SECRET)

VALID_SIDES = {"BUY", "SELL"}

def place_order(symbol, side, qty):
    if side not in VALID_SIDES:
        send_telegram(f"⚠️ Invalid order side: {side}")
        return None
    if qty <= 0:
        send_telegram(f"⚠️ Invalid quantity: {qty}")
        return None

    if MODE == "SAFE":
        print(f"[SIM] {side} {symbol} {qty}")
        send_telegram(f"🟡 SIM {side} {symbol} {qty}")
    else:
        try:
            order = client.create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=qty
            )
            send_telegram(f"🔴 LIVE {side} {symbol}")
            return order
        except BinanceAPIException as e:
            send_telegram(f"❌ Order failed: {e.message}")
            return None
