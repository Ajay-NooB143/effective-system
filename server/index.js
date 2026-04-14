require('dotenv').config();
const express = require('express');
const cors = require('cors');
const binanceRouter = require('./routes/binance');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/binance', binanceRouter);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
