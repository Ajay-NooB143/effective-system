# TradingView Webhook Setup

## Step 1: Create Alert in TradingView
1. Open TradingView chart
2. Click **Alerts** → **Create Alert**
3. Set your condition (e.g. EMA crossover)

## Step 2: Set Webhook URL
In the alert settings, under **Notifications**:
- Enable **Webhook URL**
- Enter: `http://YOUR_SERVER_IP:5000/webhook`

> **Optional security:** Set `WEBHOOK_SECRET` in your `.env` and add the header
> `X-Webhook-Secret: your_webhook_secret_here` in TradingView's webhook settings.

## Step 3: Set Alert Message (JSON)
```json
{
  "symbol": "{{ticker}}",
  "price": "{{close}}"
}
```

## Step 4: Save Alert
TradingView will now POST to your bot on every alert! ✅
