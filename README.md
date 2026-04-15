# effective-system

A trading dashboard with React frontend and Node.js/Express backend,
plus a Python-based algorithmic trading pipeline driven by TradingView alerts.

## Architecture

```
TradingView Alert (RSI + ATR + Volume + Price)
              ↓
       Flask /webhook  (python/app.py)
              ↓
    ┌─────────────────┐
    │  RiskManager    │  ← can_trade()? → BLOCK + Telegram alert
    │ (risk_manager)  │
    └─────────────────┘
              ↓ ALLOWED
    ┌─────────────────────────────────────┐
    │         MODEL ENSEMBLE              │
    │  XGBoost  (ml_model.py)  → signal  │
    │  Transformer (PyTorch)   → signal  │
    │  RL Agent (Q-Table)      → action  │
    │  combine_models()        → FINAL   │
    └─────────────────────────────────────┘
              ↓
    ┌─────────────────┐
    │  Portfolio      │  ← allocate() across BTC/ETH/XAUUSD/EURUSD
    │ (portfolio.py)  │
    └─────────────────┘
              ↓
    ┌─────────────────┐
    │  OrderBook      │  ← spread + imbalance features
    │ (orderbook.py)  │
    └─────────────────┘
              ↓
    ┌─────────────────┐
    │ execute_multi() │  ← SAFE sim / LIVE Binance
    │ (execution.py)  │
    └─────────────────┘
              ↓
    ┌─────────────────┐
    │  RL.update()    │  ← reward feedback loop
    │  PPO (SB3)      │  ← TradingEnv simulation
    └─────────────────┘
              ↓
         Telegram 📱
              ↓
    ┌─────────────────┐
    │  Retrain Job    │  ← schedule.every(7).days
    │  (retrain.py)   │
    └─────────────────┘
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+

### Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your API keys:
   ```
   cp .env.example .env
   ```

---

## Node.js / React dashboard

### Running the Backend
```bash
cd server
npm install
npm start
```
The server runs on `http://localhost:5000`.

### Running the Frontend
```bash
cd client
npm install
npm run dev
```
The UI runs on `http://localhost:5173`.

---

## Python Trading Pipeline

### Install dependencies
```bash
cd python
pip install -r requirements.txt
```

### Running the Flask webhook
```bash
cd python
python app.py
```
The webhook listens on `http://localhost:5001` (configurable via `FLASK_PORT`).

### Sending a TradingView alert (example payload)
```json
{
  "symbol":  "BTCUSDT",
  "rsi":     58.4,
  "atr":     340.2,
  "volume":  124500,
  "price":   67000
}
```
POST this JSON to `http://your-server:5001/webhook`.

### Running the retrain scheduler (optional, separate process)
```bash
cd python
python retrain.py
```
Retrains all models immediately and then every `RETRAIN_INTERVAL_DAYS` days.

### Trading modes
| `TRADING_MODE` | Behaviour |
|---|---|
| `sim` (default) | Paper-trades; no real orders placed |
| `live` | Places real market orders on Binance — **use with caution** |

---

## Binance Integration

### Setup
1. Create a Binance API key at https://www.binance.com/en/my/settings/api-management
   - Enable **Read Only** permissions for the balance checker
   - Enable **Spot & Margin Trading** only when `TRADING_MODE=live`
2. Add to your `.env` file:
   ```
   BINANCE_API_KEY=your_key_here
   BINANCE_SECRET_KEY=your_secret_here
   ```
3. Start the server and open the Dashboard in your browser to see your balances.

⚠️ **Security Tips:**
- Only enable **Read** permissions when not trading live
- Never share your API keys
- Never commit your `.env` file to git


