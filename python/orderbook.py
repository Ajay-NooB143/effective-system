"""OrderBook — computes spread and order-book imbalance features.

These features are injected into every model call so the ensemble can
account for current market microstructure.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class OrderBook:
    """Maintains the best bids and asks for a single symbol.

    Parameters
    ----------
    depth:
        Number of price levels to track on each side.
    """

    depth: int = 5
    bids: List[Tuple[float, float]] = field(default_factory=list)  # [(price, qty), ...]
    asks: List[Tuple[float, float]] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def update(
        self,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
    ) -> None:
        """Replace the current order-book snapshot with new bid/ask levels.

        Each side is sorted (bids descending, asks ascending) and trimmed
        to ``self.depth`` levels.
        """
        self.bids = sorted(bids, key=lambda x: -x[0])[: self.depth]
        self.asks = sorted(asks, key=lambda x: x[0])[: self.depth]

    # ------------------------------------------------------------------
    # Feature computation
    # ------------------------------------------------------------------

    def spread(self) -> float:
        """Best-ask minus best-bid.  Returns 0 when the book is empty."""
        if not self.bids or not self.asks:
            return 0.0
        return float(self.asks[0][0] - self.bids[0][0])

    def mid_price(self) -> float:
        """Mid-point between best bid and best ask."""
        if not self.bids or not self.asks:
            return 0.0
        return float((self.bids[0][0] + self.asks[0][0]) / 2)

    def imbalance(self) -> float:
        """Order-book imbalance in [-1, 1].

        Positive → more bid volume (buying pressure).
        Negative → more ask volume (selling pressure).
        """
        bid_vol = sum(qty for _, qty in self.bids)
        ask_vol = sum(qty for _, qty in self.asks)
        total = bid_vol + ask_vol
        if total == 0:
            return 0.0
        return float((bid_vol - ask_vol) / total)

    def features(self) -> dict:
        """Return a feature dict ready to be merged with market data."""
        return {
            "spread": self.spread(),
            "imbalance": self.imbalance(),
            "mid_price": self.mid_price(),
        }
