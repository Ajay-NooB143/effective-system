"""Signals-only bot execution adapter. Broker submission is disabled."""


def place_order(symbol, side, qty):
    """Return a signal record; never contact Binance or another broker."""
    if side not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")
    if not symbol or float(qty) <= 0:
        raise ValueError("symbol and positive quantity are required")
    return {
        "status": "signal_only",
        "symbol": str(symbol),
        "side": side,
        "quantity": float(qty),
        "execution": "disabled",
    }
