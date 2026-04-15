import datetime

class RiskManager:
    def __init__(self, max_daily_loss=5, risk_per_trade=0.02, max_trades=5):
        self.max_daily_loss = max_daily_loss   # % max loss per day
        self.risk_per_trade = risk_per_trade   # % of balance risked per trade
        self.max_trades = max_trades           # max trades allowed per day

        self.start_balance = 1000
        self.current_balance = 1000
        self.trades_today = 0
        self.last_day = datetime.date.today()

    def reset_daily(self):
        today = datetime.date.today()
        if today != self.last_day:
            self.trades_today = 0
            self.start_balance = self.current_balance
            self.last_day = today

    def can_trade(self):
        self.reset_daily()

        daily_loss = ((self.current_balance - self.start_balance) / self.start_balance) * 100

        if daily_loss < -self.max_daily_loss:
            return False, "❌ Max daily loss reached"

        if self.trades_today >= self.max_trades:
            return False, "❌ Max trades reached for today"

        return True, "✅ Allowed"

    def position_size(self, price):
        risk_amount = self.current_balance * self.risk_per_trade
        qty = risk_amount / price
        return round(qty, 5)

    def update_balance(self, pnl):
        self.current_balance += pnl
        self.trades_today += 1
