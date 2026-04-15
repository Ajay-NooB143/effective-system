from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_SECRET, MODE
from telegram_bot import send_telegram

client = Client(BINANCE_API_KEY, BINANCE_SECRET)

def place_order(symbol, side, qty):
    if MODE == "SAFE":
        print(f"[SIM] {side} {symbol} {qty}")
        send_telegram(f"🟡 SIM {side} {symbol} qty={qty}")
    else:
        try:
            order = client.create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=qty
            )
            send_telegram(f"✅ LIVE ORDER PLACED\n{side} {symbol}\nQty: {qty}")
            return order
        except Exception as e:
            send_telegram(f"❌ ORDER FAILED: {e}")
            print(f"[Order Error] {e}")
