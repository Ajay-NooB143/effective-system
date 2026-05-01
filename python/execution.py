"""Order execution — simulation, live Binance, or ZMQ bridge modes.

Set the environment variable ``TRADING_MODE`` to choose the execution path:

* ``sim`` (default) — paper-trades; no real orders placed.
* ``live``          — places real market orders directly via python-binance.
* ``zmq``           — forwards orders to the C++ execution engine through the
                      ZMQ PUSH bridge (see ``execution/bridge.py``).
                      The C++ engine handles signing and Binance REST calls.
"""

import os
import sys
from typing import Dict

from telegram_bot import send_message

TRADING_MODE = os.getenv("TRADING_MODE", "sim").lower()

# Add repo root to sys.path so ``execution.bridge`` is importable when
# running from the ``python/`` directory.
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    from binance.client import Client as BinanceClient  # type: ignore
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False

_binance_client = None


def _get_binance_client():
    global _binance_client
    if _binance_client is None:
        if not BINANCE_AVAILABLE:
            raise ImportError(
                "python-binance is not installed. "
                "Run: pip install python-binance"
            )
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_SECRET_KEY", "")
        _binance_client = BinanceClient(api_key, api_secret)
    return _binance_client


def execute_multi(allocations: Dict[str, float], prices: Dict[str, float]) -> list:
    """Execute orders for all symbols with non-zero allocation.

    Parameters
    ----------
    allocations:
        Mapping ``{symbol: notional}`` produced by ``Portfolio.allocate()``.
        Positive notional = buy, negative = sell.
    prices:
        Current prices per symbol (used to compute quantities).

    Returns
    -------
    List of order result dicts (one per executed symbol).
    """
    results = []
    for symbol, notional in allocations.items():
        if notional == 0:
            continue

        price = prices.get(symbol, 0)
        if price <= 0:
            continue

        quantity = abs(notional) / price
        side = "BUY" if notional > 0 else "SELL"

        if TRADING_MODE == "live":
            result = _execute_live(symbol, side, quantity)
        elif TRADING_MODE == "zmq":
            result = _execute_zmq(symbol, side, quantity)
        else:
            result = _execute_sim(symbol, side, quantity, price)

        results.append(result)
        _notify(result)

    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _execute_sim(symbol: str, side: str, quantity: float, price: float) -> dict:
    """Return a simulated order result."""
    return {
        "mode": "sim",
        "symbol": symbol,
        "side": side,
        "quantity": round(quantity, 6),
        "price": price,
        "status": "FILLED",
    }


def _execute_live(symbol: str, side: str, quantity: float) -> dict:
    """Place a live market order on Binance and return the response."""
    client = _get_binance_client()
    try:
        order = client.order_market(
            symbol=symbol,
            side=side,
            quantity=round(quantity, 6),
        )
        return {
            "mode": "live",
            "symbol": symbol,
            "side": side,
            "quantity": round(quantity, 6),
            "orderId": order.get("orderId"),
            "status": order.get("status", "UNKNOWN"),
        }
    except Exception as exc:
        return {
            "mode": "live",
            "symbol": symbol,
            "side": side,
            "quantity": round(quantity, 6),
            "status": "ERROR",
            "error": str(exc),
        }


def _execute_zmq(symbol: str, side: str, quantity: float) -> dict:
    """Forward the order to the C++ execution engine via ZMQ PUSH bridge."""
    try:
        from execution.bridge import send_order  # type: ignore[import]

        send_order(symbol, side, round(quantity, 6))
        return {
            "mode": "zmq",
            "symbol": symbol,
            "side": side,
            "quantity": round(quantity, 6),
            "status": "SENT",
        }
    except Exception as exc:
        return {
            "mode": "zmq",
            "symbol": symbol,
            "side": side,
            "quantity": round(quantity, 6),
            "status": "ERROR",
            "error": str(exc),
        }


def _notify(result: dict) -> None:
    mode = result["mode"]
    mode_tag = {"sim": "🟡 SIM", "live": "🟢 LIVE", "zmq": "🔵 ZMQ"}.get(
        mode, mode.upper()
    )
    status = result.get("status", "?")
    symbol = result.get("symbol", "?")
    side = result.get("side", "?")
    qty = result.get("quantity", 0)
    price = result.get("price") or result.get("orderId", "")

    if result.get("error"):
        msg = (
            f"❌ {mode_tag} order FAILED\n"
            f"Symbol: {symbol}  Side: {side}  Qty: {qty}\n"
            f"Error: {result['error']}"
        )
    else:
        msg = (
            f"✅ {mode_tag} order {status}\n"
            f"Symbol: {symbol}  Side: {side}  Qty: {qty}"
        )
        if price:
            msg += f"  Ref: {price}"

    send_message(msg)
