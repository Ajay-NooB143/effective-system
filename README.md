# effective-system

A trading dashboard with React frontend and Node.js/Express backend.

## Getting Started

### Prerequisites
- Node.js 18+

### Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your API keys:
   ```
   cp .env.example .env
   ```

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

## Binance Integration

### Setup
1. Create a Binance API key at https://www.binance.com/en/my/settings/api-management
   - Enable **Read Only** permissions (no trading permissions needed for balance check)
2. Add to your `.env` file in the `server/` directory:
   ```
   BINANCE_API_KEY=your_key_here
   BINANCE_SECRET_KEY=your_secret_here
   ```
3. Start the server and open the Dashboard in your browser to see your balances.

⚠️ **Security Tips:**
- Only enable **Read** permissions on your Binance API key
- Never share your API keys
- Never commit your `.env` file to git

---

## 💀 Ajay AI Trading Bot

### Pipeline
TradingView Alert → Webhook → ai_predict() (GPT-4) → Binance Order → Telegram

### Setup
1. Copy `.env.example` to `.env` and fill in your keys
2. Install dependencies:
   ```bash
   cd bot
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python main.py
   ```
4. Set TradingView webhook to: `http://YOUR_SERVER_IP:5000/webhook`
5. Set alert message JSON:
   ```json
   { "symbol": "{{ticker}}", "price": "{{close}}" }
   ```

### Modes
- `MODE=SAFE` → Simulates trades (no real orders)
- `MODE=LIVE` → Places real Binance orders ⚠️

### ⚠️ Security
- Never share your `.env` file
- Never commit API keys to git
- Use READ + TRADE permissions on Binance API key for LIVE mode
- Use READ ONLY for SAFE mode
