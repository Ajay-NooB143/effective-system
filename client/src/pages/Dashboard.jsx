import BinanceBalance from '../components/BinanceBalance';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <header className="conva-header">
        <h1 className="conva-title">CONVA</h1>
        <p className="conva-tagline">Built for AI</p>
      </header>
      <BinanceBalance />
    </div>
  );
};

export default Dashboard;
