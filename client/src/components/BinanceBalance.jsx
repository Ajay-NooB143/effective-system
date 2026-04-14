import { useEffect, useState } from 'react';
import axios from 'axios';

const BinanceBalance = () => {
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('/api/binance/balance')
      .then((res) => {
        setBalances(res.data.balances);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to fetch balance. Check your API keys.');
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading balances...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div className="binance-balance">
      <h2>💰 Binance Spot Balance</h2>
      <table>
        <thead>
          <tr>
            <th>Asset</th>
            <th>Free</th>
            <th>Locked</th>
          </tr>
        </thead>
        <tbody>
          {balances.map((b) => (
            <tr key={b.asset}>
              <td>{b.asset}</td>
              <td>{parseFloat(b.free).toFixed(6)}</td>
              <td>{parseFloat(b.locked).toFixed(6)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BinanceBalance;
