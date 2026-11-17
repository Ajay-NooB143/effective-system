"""Disabled ZMQ order bridge.

This repository is configured for signal generation only. Any attempt to
forward an order to the C++ execution service fails closed.
"""


def send_order(*args, **kwargs) -> None:
    raise RuntimeError("Order forwarding is disabled: signals-only mode")
