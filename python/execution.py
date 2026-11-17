"""Signals-only execution facade.

The historical module name is retained for import compatibility. No broker
client is imported and no simulated or live order is submitted.
"""
from typing import Dict


def execute_multi(allocations: Dict[str, float], prices: Dict[str, float]) -> list:
    """Convert non-zero allocations into signal records only."""
    results = []
    for symbol, notional in allocations.items():
        try:
            amount = float(notional)
            price = float(prices.get(symbol, 0))
        except (TypeError, ValueError):
            continue
        if amount == 0 or price <= 0:
            continue
        results.append({
            "status": "signal_only",
            "symbol": str(symbol),
            "side": "BUY" if amount > 0 else "SELL",
            "notional": abs(amount),
            "reference_price": price,
            "execution": "disabled",
        })
    return results
