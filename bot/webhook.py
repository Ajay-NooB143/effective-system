"""Authenticated signal-only webhook."""
import hmac
from flask import Flask, request, abort, jsonify
from ai_model import ai_predict
from telegram_bot import send_telegram
from config import WEBHOOK_SECRET

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    if not WEBHOOK_SECRET:
        abort(503, description="Webhook authentication is not configured")
    token = request.headers.get("X-Webhook-Secret", "")
    if not hmac.compare_digest(token, str(WEBHOOK_SECRET)):
        abort(403)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="Invalid or missing JSON payload")

    symbol = str(data.get("symbol", "")).strip().upper()
    try:
        price = float(data.get("price", 0))
    except (TypeError, ValueError):
        abort(400, description="Invalid price")
    if not symbol or price <= 0:
        abort(400, description="symbol and positive price are required")

    signal, confidence = ai_predict([price])
    label = signal if signal in ("BUY", "SELL", "HOLD") else "HOLD"
    send_telegram(
        f"📡 SIGNAL ONLY: {label}\nSymbol: {symbol}\nPrice: {price}\n"
        f"Confidence: {round(float(confidence) * 100, 2)}%\nExecution: DISABLED"
    )
    return jsonify({
        "status": "signal_only",
        "symbol": symbol,
        "signal": label,
        "confidence": float(confidence),
        "execution": "disabled",
    }), 200


if __name__ == "__main__":
    app.run(port=5000)
