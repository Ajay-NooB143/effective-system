# Effective System — Trading Tour

An interactive trading education system with a CLI agent, a Node.js/Express AI backend,
and a Vite + React web UI.

## Setup

### Backend (Python CLI)

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
python main.py /_learn
```

### Server (Node.js)

```bash
cd server
npm install
node index.js
```

### Web UI

```bash
cd client
npm install
npm run dev
```

Open <http://localhost:3000> in Chrome.

## API

- `POST /api/ai/chat` — Ask GPT-4 a trading question

  **Request body:**
  ```json
  { "message": "What is an order block?", "context": "Order Blocks stop" }
  ```

  **Response:**
  ```json
  { "reply": "An order block is..." }
  ```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
OPENAI_API_KEY=your_openai_api_key_here
PORT=5000
```

> ⚠️ Never commit `.env` to git — it is listed in `.gitignore`.