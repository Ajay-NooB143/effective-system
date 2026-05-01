"""ZMQ PUSH bridge — forwards order messages to the C++ execution engine.

This module is used by ``python/execution.py`` when ``TRADING_MODE=zmq``.
It can also be imported standalone::

    from execution.bridge import send_order
    send_order("BTCUSDT", "BUY", 0.001)

Environment variables
---------------------
ZMQ_ENDPOINT : str
    ZMQ PUSH endpoint to connect to (default: ``tcp://localhost:5555``).
"""

import os
from typing import Optional

ZMQ_ENDPOINT: str = os.getenv("ZMQ_ENDPOINT", "tcp://localhost:5555")

_ctx: Optional[object] = None
_sock: Optional[object] = None


def _get_socket():
    """Lazily initialise and return the ZMQ PUSH socket."""
    global _ctx, _sock
    if _sock is None:
        import zmq  # deferred so the module loads even without pyzmq installed

        _ctx = zmq.Context()
        _sock = _ctx.socket(zmq.PUSH)
        _sock.connect(ZMQ_ENDPOINT)
    return _sock


def send_order(
    symbol: str,
    side: str,
    qty: float,
    order_type: str = "MARKET",
    time_in_force: str = "GTC",
) -> None:
    """Send an order message to the C++ execution engine.

    Parameters
    ----------
    symbol:
        Binance symbol, e.g. ``"BTCUSDT"``.
    side:
        ``"BUY"`` or ``"SELL"``.
    qty:
        Absolute quantity in base-asset units (must be > 0).
    order_type:
        Order type (default: ``"MARKET"``).
    time_in_force:
        Time-in-force flag forwarded to the engine (default: ``"GTC"``).
        Ignored by Binance for MARKET orders.

    Raises
    ------
    ValueError
        If ``symbol`` is empty, ``side`` is invalid, or ``qty`` is not
        positive.
    """
    if not symbol:
        raise ValueError("symbol must be non-empty")
    if side not in ("BUY", "SELL"):
        raise ValueError(f"side must be 'BUY' or 'SELL', got {side!r}")
    if qty <= 0:
        raise ValueError(f"qty must be > 0, got {qty}")

    msg = {
        "symbol": symbol,
        "side": side,
        "qty": round(qty, 8),
        "type": order_type,
        "timeInForce": time_in_force,
    }
    _get_socket().send_json(msg)
