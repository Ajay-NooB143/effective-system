"""Order execution — safe simulation mode and live Binance mode.

Set the environment variable ``TRADING_MODE=live`` to switch from
simulation to real Binance orders.  All other values (or absence of
the variable) keep the system in safe simulation mode.
"""

import os
from typing import Dict

from telegram_bot import send_message

TRADING_MODE = os.getenv("TRADING_MODE", "sim").lower()

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
                "python-binance is not installed. " "Run: pip install python-binance"
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


def _notify(result: dict) -> None:
    mode_tag = "🟡 SIM" if result["mode"] == "sim" else "🟢 LIVE"
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
