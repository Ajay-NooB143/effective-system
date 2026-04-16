"""Portfolio allocator — distributes capital across multiple assets.

Supported symbols: BTC/USDT, ETH/USDT, XAUUSD, EURUSD (configurable via env).
"""

import os
from typing import Dict

SUPPORTED_SYMBOLS = [
    s.strip()
    for s in os.getenv("PORTFOLIO_SYMBOLS", "BTCUSDT,ETHUSDT,XAUUSD,EURUSD").split(",")
]

# Minimum allocation weight per symbol (0–1).  Remaining capital is split
# equally among symbols that have an active signal.
MIN_WEIGHT = float(os.getenv("PORTFOLIO_MIN_WEIGHT", "0.0"))


class Portfolio:
    """Equal-weight capital allocator with per-symbol position tracking."""

    def __init__(
        self,
        symbols: list = None,
        initial_balance: float = float(os.getenv("INITIAL_BALANCE", "10000")),
    ) -> None:
        self.symbols = symbols or SUPPORTED_SYMBOLS
        self.balance = initial_balance
        self._positions: Dict[str, float] = {s: 0.0 for s in self.symbols}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allocate(self, signals: Dict[str, int]) -> Dict[str, float]:
        """Compute notional size for each symbol given directional signals.

        Parameters
        ----------
        signals:
            Mapping ``{symbol: signal}`` where signal ∈ {-1, 0, 1}.

        Returns
        -------
        Dict mapping each symbol to its proposed notional trade size
        (positive = long, negative = short, zero = no trade).
        """
        active = {s: sig for s, sig in signals.items() if sig != 0}
        n_active = len(active)

        if n_active == 0:
            return {s: 0.0 for s in self.symbols}

        weight_per_symbol = max(MIN_WEIGHT, 1.0 / n_active)

        allocations: Dict[str, float] = {}
        for symbol in self.symbols:
            sig = signals.get(symbol, 0)
            if sig == 0:
                allocations[symbol] = 0.0
            else:
                notional = self.balance * weight_per_symbol
                allocations[symbol] = float(sig) * notional

        return allocations

    def update_position(self, symbol: str, delta: float) -> None:
        """Adjust the tracked position for *symbol* by *delta* units."""
        self._positions[symbol] = self._positions.get(symbol, 0.0) + delta

    def get_position(self, symbol: str) -> float:
        return self._positions.get(symbol, 0.0)

    def update_balance(self, new_balance: float) -> None:
        self.balance = new_balance

    @property
    def positions(self) -> Dict[str, float]:
        return dict(self._positions)
