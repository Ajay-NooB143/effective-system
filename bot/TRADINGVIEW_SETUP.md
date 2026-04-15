# TradingView Setup Guide

## How to Connect TradingView to the Bot

### Step 1: Create an Alert
1. Open any chart on TradingView
2. Click the **Alerts** icon (bell icon)
3. Set your alert condition (e.g., RSI crossover, EMA cross, etc.)

### Step 2: Configure Webhook
1. In the Alert settings, go to **Notifications**
2. Enable **Webhook URL**
3. Enter your server URL: `http://YOUR_SERVER_IP:5000/webhook`

### Step 3: Set Alert Message
Paste this JSON in the alert message box:
```json
{
  "symbol": "{{ticker}}",
  "price": "{{close}}"
}
```

### Step 4: Save and Test
1. Save the alert
2. Check your Telegram for a notification
3. Verify the bot received the signal

---

## Risk Management
The bot includes automatic risk management:
| Setting | Default | Description |
|---------|---------|-------------|
| `max_daily_loss` | 5% | Bot stops if daily loss exceeds 5% |
| `risk_per_trade` | 2% | 2% of balance risked per trade |
| `max_trades` | 5 | Max 5 trades per day |

Position size is automatically calculated based on your current balance and price.

---

## Notes
- Requires **TradingView Pro** or higher for webhook alerts
- Make sure your server is publicly accessible (use ngrok for testing)
- Start with `MODE=SAFE` in your `.env` for paper trading
