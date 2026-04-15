from flask import Flask, request
from ai_model import ai_predict
from telegram_bot import send_telegram
from execution import place_order
from risk_manager import RiskManager

app = Flask(__name__)
risk = RiskManager()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    symbol = data.get("symbol", "BTCUSDT")
    price  = float(data.get("price", 0))

    if price <= 0:
        return "INVALID PRICE", 400

    # 1. Risk check FIRST
    allowed, reason = risk.can_trade()
    if not allowed:
        send_telegram(f"""
🛑 TRADE BLOCKED
📊 Symbol: {symbol}
💰 Price: {price}
⚠️ Reason: {reason}
💵 Balance: ${round(risk.current_balance, 2)}
📉 Trades Today: {risk.trades_today}/{risk.max_trades}
""")
        return "BLOCKED", 200

    # 2. AI prediction
    features = [price]
    signal, confidence = ai_predict(features)

    if signal != "HOLD":
        # 3. Dynamic position size from RiskManager
        qty = risk.position_size(price)

        place_order(symbol, signal, qty)

        # 4. Update balance (simulate PnL as 0 for now)
        risk.update_balance(0)

        send_telegram(f"""
💀 SIGNAL: {signal}
📊 Symbol: {symbol}
💰 Price: {price}
🧠 Confidence: {round(confidence * 100, 2)}%
📦 Qty: {qty}
💵 Balance: ${round(risk.current_balance, 2)}
📉 Trades Today: {risk.trades_today}/{risk.max_trades}
""")
    else:
        send_telegram(f"""
🟡 HOLD — No trade
📊 Symbol: {symbol}
💰 Price: {price}
🧠 Confidence: {round(confidence * 100, 2)}%
💵 Balance: ${round(risk.current_balance, 2)}
""")

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
