const express = require('express');
const router = express.Router();
const { getSpotBalance } = require('../controllers/binanceController');

// GET /api/binance/balance
router.get('/balance', getSpotBalance);

module.exports = router;
