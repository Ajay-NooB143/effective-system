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
