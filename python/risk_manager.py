"""Fail-closed portfolio risk gate for signal generation."""
import math
from datetime import date


class RiskManager:
    def __init__(self, max_daily_loss=0.05, max_drawdown=0.10,
                 max_position_pct=0.20):
        self.max_daily_loss = float(max_daily_loss)
        self.max_drawdown = float(max_drawdown)
        self.max_position_pct = float(max_position_pct)
        limits = (self.max_daily_loss, self.max_drawdown, self.max_position_pct)
        if not all(math.isfinite(x) and 0 < x <= 1 for x in limits):
            raise ValueError("risk limits must be finite fractions in (0, 1]")
        self._daily_loss = 0.0
        self._last_reset = date.today()

    def can_trade(self, symbol, proposed_size, portfolio_value,
                  current_drawdown=0.0):
        self._maybe_reset_daily()
        try:
            size = float(proposed_size)
            value = float(portfolio_value)
            drawdown = float(current_drawdown)
        except (TypeError, ValueError):
            return False
        if not all(math.isfinite(x) for x in (size, value, drawdown)):
            return False
        if value <= 0 or size <= 0 or drawdown < 0:
            return False
        if size / value > self.max_position_pct:
            return False
        if self._daily_loss / value >= self.max_daily_loss:
            return False
        if drawdown >= self.max_drawdown:
            return False
        return True

    def record_loss(self, loss_amount):
        self._maybe_reset_daily()
        amount = float(loss_amount)
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("loss amount must be finite and non-negative")
        self._daily_loss += amount

    @property
    def daily_loss(self):
        self._maybe_reset_daily()
        return self._daily_loss

    def _maybe_reset_daily(self):
        today = date.today()
        if today != self._last_reset:
            self._daily_loss = 0.0
            self._last_reset = today
