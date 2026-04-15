from config import BINANCE_API_KEY, BINANCE_SECRET, MODE, TELEGRAM_TOKEN, CHAT_ID
from binance.client import Client
from telegram_bot import send_telegram

client = Client(BINANCE_API_KEY, BINANCE_SECRET)

def place_order(symbol, side, qty):
    if MODE == "SAFE":
        print(f"[SIM] {side} {symbol} {qty}")
        send_telegram(f"🟡 SIM {side} {symbol} {qty}")
    else:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=qty
        )
        send_telegram(f"🔴 LIVE {side} {symbol}")
        return order
