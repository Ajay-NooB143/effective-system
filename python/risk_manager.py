"""RiskManager — gate-keeps every trade attempt.

Usage
-----
    from risk_manager import RiskManager

    rm = RiskManager(max_daily_loss=0.05, max_drawdown=0.10, max_position_pct=0.20)
    if rm.can_trade(symbol, proposed_size, portfolio_value, current_drawdown):
        ...  # proceed
"""

import os
from datetime import date
from telegram_bot import send_message


class RiskManager:
    """Enforces daily-loss, drawdown, and position-size limits."""

    def __init__(
        self,
        max_daily_loss: float = float(os.getenv("MAX_DAILY_LOSS", "0.05")),
        max_drawdown: float = float(os.getenv("MAX_DRAWDOWN", "0.10")),
        max_position_pct: float = float(os.getenv("MAX_POSITION_PCT", "0.20")),
    ) -> None:
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.max_position_pct = max_position_pct

        self._daily_loss: float = 0.0
        self._last_reset: date = date.today()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def can_trade(
        self,
        symbol: str,
        proposed_size: float,
        portfolio_value: float,
        current_drawdown: float = 0.0,
    ) -> bool:
        """Return True if the proposed trade passes all risk checks.

        Sends a Telegram alert and returns False when any limit is breached.
        """
        self._maybe_reset_daily()

        reason = self._check(proposed_size, portfolio_value, current_drawdown)
        if reason:
            msg = (
                f"🚫 <b>Trade BLOCKED</b>\n"
                f"Symbol: {symbol}\n"
                f"Size: {proposed_size:.4f}\n"
                f"Reason: {reason}"
            )
            send_message(msg)
            return False

        return True

    def record_loss(self, loss_amount: float) -> None:
        """Call after a closed losing trade to update the daily loss tally."""
        self._maybe_reset_daily()
        if loss_amount > 0:
            self._daily_loss += loss_amount

    @property
    def daily_loss(self) -> float:
        self._maybe_reset_daily()
        return self._daily_loss

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check(
        self, proposed_size: float, portfolio_value: float, current_drawdown: float
    ) -> str:
        """Return a non-empty reason string when a limit is breached."""
        if portfolio_value <= 0:
            return "portfolio value is zero or negative"

        position_pct = proposed_size / portfolio_value
        if position_pct > self.max_position_pct:
            return (
                f"position size {position_pct:.1%} exceeds limit "
                f"{self.max_position_pct:.1%}"
            )

        daily_loss_pct = self._daily_loss / portfolio_value
        if daily_loss_pct >= self.max_daily_loss:
            return (
                f"daily loss {daily_loss_pct:.1%} has reached limit "
                f"{self.max_daily_loss:.1%}"
            )

        if current_drawdown >= self.max_drawdown:
            return (
                f"drawdown {current_drawdown:.1%} has reached limit "
                f"{self.max_drawdown:.1%}"
            )

        return ""

    def _maybe_reset_daily(self) -> None:
        today = date.today()
        if today != self._last_reset:
            self._daily_loss = 0.0
            self._last_reset = today
