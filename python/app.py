"""Flask webhook — TradingView alert entry point.

Expected JSON payload from TradingView:
    {
        "symbol":   "BTCUSDT",
        "rsi":      55.3,
        "atr":      120.4,
        "volume":   98234.0,
        "price":    67000.0,

        // optional — supplied by the orderbook update endpoint
        "spread":     10.0,
        "imbalance":  0.15
    }

Endpoints
---------
POST /webhook          — main alert handler
POST /orderbook/update — update the in-memory order book for a symbol
GET  /health           — liveness probe
"""

import logging
import os
from typing import Dict

from flask import Flask, jsonify, request

from combine_models import combine_models
from execution import execute_multi
from ml_model import XGBoostModel
from orderbook import OrderBook
from portfolio import Portfolio
from retrain import RETRAIN_DATA
from risk_manager import RiskManager
from rl_agent import RLAgent
from telegram_bot import send_message
from transformer_model import TransformerModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application-level singletons
# ---------------------------------------------------------------------------

app = Flask(__name__)

risk_manager = RiskManager()
portfolio = Portfolio()

xgb_model = XGBoostModel()
transformer = TransformerModel()
rl_agent = RLAgent()

# Per-symbol order books
order_books: Dict[str, OrderBook] = {}

# Rolling feature window per symbol (for the Transformer)
feature_windows: Dict[str, list] = {}

# Track last features per symbol for RL reward feedback
_last_features: Dict[str, dict] = {}
_last_action: Dict[str, int] = {}

# Attempt to load pre-trained models (silently skip if not found)
for _loader, _path_env, _default in [
    (xgb_model.load, "XGBOOST_MODEL_PATH", "models/xgboost_model.pkl"),
    (transformer.load, "TRANSFORMER_MODEL_PATH", "models/transformer_model.pt"),
    (rl_agent.load_qtable, "QTABLE_PATH", "models/qtable.pkl"),
]:
    try:
        _loader()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/orderbook/update", methods=["POST"])
def orderbook_update():
    """Accept a live order-book snapshot for a symbol."""
    data = request.get_json(force=True) or {}
    symbol = data.get("symbol", "").upper()
    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    bids = [(float(b[0]), float(b[1])) for b in data.get("bids", [])]
    asks = [(float(a[0]), float(a[1])) for a in data.get("asks", [])]

    if symbol not in order_books:
        order_books[symbol] = OrderBook()

    order_books[symbol].update(bids, asks)
    return jsonify({"status": "updated", "symbol": symbol})


@app.route("/webhook", methods=["POST"])
def webhook():
    """Main TradingView alert handler."""
    try:
        return _process_webhook()
    except Exception as exc:
        logger.exception("Unhandled error in /webhook")
        return jsonify({"error": "internal server error"}), 500


def _process_webhook():
    data = request.get_json(force=True) or {}

    symbol = str(data.get("symbol", "")).upper()
    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    # Build feature dict — merge market data with order-book features
    ob = order_books.get(symbol, OrderBook())
    features = {
        "symbol": symbol,
        "rsi": float(data.get("rsi", 50)),
        "atr": float(data.get("atr", 0)),
        "volume": float(data.get("volume", 0)),
        "price": float(data.get("price", 0)),
        **ob.features(),
    }
    # Allow explicit override from payload
    if "spread" in data:
        features["spread"] = float(data["spread"])
    if "imbalance" in data:
        features["imbalance"] = float(data["imbalance"])

    price = features["price"]

    # RL reward feedback for previous step
    if symbol in _last_features and symbol in _last_action:
        prev_price = float(_last_features[symbol].get("price", price))
        pct_change = (price - prev_price) / (prev_price + 1e-9)
        reward = pct_change * _last_action[symbol]
        rl_agent.update(_last_features[symbol], _last_action[symbol], reward, features)

    # -----------------------------------------------------------------
    # Risk gate
    # -----------------------------------------------------------------
    portfolio_value = portfolio.balance
    proposed_size = portfolio_value * float(os.getenv("ALERT_POSITION_PCT", "0.10"))
    current_drawdown = float(data.get("drawdown", 0))

    if not risk_manager.can_trade(
        symbol, proposed_size, portfolio_value, current_drawdown
    ):
        return (
            jsonify({"status": "blocked", "symbol": symbol, "reason": "risk limit"}),
            200,
        )

    # -----------------------------------------------------------------
    # Model ensemble
    # -----------------------------------------------------------------
    if symbol not in feature_windows:
        feature_windows[symbol] = []
    feature_windows[symbol].append(features)
    feature_windows[symbol] = feature_windows[symbol][-50:]  # keep last 50

    final_signal = combine_models(
        xgb_model, transformer, rl_agent, features, feature_windows[symbol]
    )

    # Store for next RL update
    _last_features[symbol] = features
    _last_action[symbol] = final_signal

    # -----------------------------------------------------------------
    # Portfolio allocation
    # -----------------------------------------------------------------
    signals = {symbol: final_signal}
    allocations = portfolio.allocate(signals)

    # -----------------------------------------------------------------
    # Execution
    # -----------------------------------------------------------------
    prices = {symbol: price}
    results = execute_multi(allocations, prices)

    # -----------------------------------------------------------------
    # Retrain data buffer
    # -----------------------------------------------------------------
    RETRAIN_DATA.append({**features, "label": final_signal})
    if len(RETRAIN_DATA) > 10_000:
        RETRAIN_DATA.pop(0)

    # -----------------------------------------------------------------
    # Telegram summary
    # -----------------------------------------------------------------
    signal_label = {1: "🟢 LONG", -1: "🔴 SHORT", 0: "⚪ FLAT"}.get(final_signal, "?")
    send_message(
        f"📡 <b>Alert processed</b>\n"
        f"Symbol: {symbol}  Signal: {signal_label}\n"
        f"RSI: {features['rsi']:.1f}  ATR: {features['atr']:.2f}  "
        f"Vol: {features['volume']:.0f}\n"
        f"Orders: {len(results)}"
    )

    return jsonify(
        {
            "status": "ok",
            "symbol": symbol,
            "signal": final_signal,
            "allocations": allocations,
            "orders": results,
        }
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=False)
