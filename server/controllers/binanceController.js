const Binance = require('binance-api-node').default;

const client = Binance({
  apiKey: process.env.BINANCE_API_KEY,
  apiSecret: process.env.BINANCE_SECRET_KEY,
});

const getSpotBalance = async (req, res) => {
  try {
    const accountInfo = await client.accountInfo();
    // Filter out zero balances
    const balances = accountInfo.balances.filter(
      (b) => parseFloat(b.free) > 0 || parseFloat(b.locked) > 0
    );
    res.json({ success: true, balances });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

module.exports = { getSpotBalance };
