from flask import Flask, request, abort
from ai_model import ai_predict
from telegram_bot import send_telegram
from execution import place_order
from config import WEBHOOK_SECRET, ORDER_QTY

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    # Validate shared secret if configured
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Webhook-Secret", "")
        if token != WEBHOOK_SECRET:
            abort(403)

    data = request.json
    if not data:
        abort(400, description="Invalid or missing JSON payload.")

    symbol = data.get("symbol", "BTCUSDT")
    try:
        price = float(data.get("price", 0))
    except (TypeError, ValueError):
        abort(400, description="Invalid 'price' value — must be a number.")

    if price <= 0:
        abort(400, description="Invalid 'price' value — must be greater than zero.")

    features = [price]

    signal, confidence = ai_predict(features)

    if signal != "HOLD":
        place_order(symbol, signal, ORDER_QTY)

        send_telegram(f"""
💀 SIGNAL: {signal}
📊 Symbol: {symbol}
💰 Price: {price}
🧠 Confidence: {round(confidence * 100, 2)}%
""")
    else:
        send_telegram(f"""
🟡 HOLD — No trade
📊 Symbol: {symbol}
💰 Price: {price}
🧠 Confidence: {round(confidence * 100, 2)}%
""")

    return "OK", 200


if __name__ == "__main__":
    app.run(port=5000)
