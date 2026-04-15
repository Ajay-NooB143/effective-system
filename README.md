# effective-system

[![CI - All Systems](https://github.com/Ajay-NooB143/effective-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Ajay-NooB143/effective-system/actions/workflows/ci.yml)
[![Python Trading Pipeline CI](https://github.com/Ajay-NooB143/effective-system/actions/workflows/python-pipeline.yml/badge.svg)](https://github.com/Ajay-NooB143/effective-system/actions/workflows/python-pipeline.yml)
[![Bot CI](https://github.com/Ajay-NooB143/effective-system/actions/workflows/bot-ci.yml/badge.svg)](https://github.com/Ajay-NooB143/effective-system/actions/workflows/bot-ci.yml)
[![Server CI](https://github.com/Ajay-NooB143/effective-system/actions/workflows/server-ci.yml/badge.svg)](https://github.com/Ajay-NooB143/effective-system/actions/workflows/server-ci.yml)
[![Client CI](https://github.com/Ajay-NooB143/effective-system/actions/workflows/client-ci.yml/badge.svg)](https://github.com/Ajay-NooB143/effective-system/actions/workflows/client-ci.yml)
[![Security Audit](https://github.com/Ajay-NooB143/effective-system/actions/workflows/security-audit.yml/badge.svg)](https://github.com/Ajay-NooB143/effective-system/actions/workflows/security-audit.yml)

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

---

## CI/CD Workflows

This repository includes comprehensive GitHub Actions workflows for continuous integration and deployment:

### Available Workflows

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| **CI - All Systems** | Tests all components in parallel | Push to main/develop, PRs |
| **Python Trading Pipeline CI** | Lints and tests Python trading pipeline | Changes to `python/` directory |
| **Bot CI** | Validates bot system | Changes to `bot/` directory |
| **Server CI** | Tests Node.js backend | Changes to `server/` directory |
| **Client CI** | Builds and tests React frontend | Changes to `client/` directory |
| **Integration Test** | End-to-end testing of all systems | Push to main, PRs, manual |
| **Security Audit** | Scans for vulnerabilities | Weekly, push to main, manual |

### Workflow Features

- ✅ **Multi-version testing**: Python 3.10-3.12, Node.js 18-22
- 🔍 **Code quality checks**: Linting (flake8, black, pylint, ESLint)
- 🧪 **Automated testing**: Unit tests and integration tests
- 🔒 **Security scanning**: Bandit, npm audit, pip-audit
- 📦 **Build validation**: Ensures all systems build correctly
- 🚀 **Import validation**: Verifies all modules import successfully

### Running Workflows Locally

You can validate your changes locally before pushing:

```bash
# Python Trading Pipeline
cd python
pip install -r requirements.txt
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
black --check .
python -c "from app import app; print('✅ Validated')"

# Bot
cd bot
pip install -r requirements.txt
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
python -c "from webhook import app; print('✅ Validated')"

# Server
cd server
npm ci
npm run lint
npm test

# Client
cd client
npm ci
npm run lint
npm run build
```

---

