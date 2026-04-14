import { Link } from "react-router-dom";
import styles from "./Home.module.css";

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.hero}>
        <h1 className={styles.title}>📈 Effective System</h1>
        <p className={styles.subtitle}>
          An interactive trading education tour powered by AI. Learn market
          structure, order blocks, fair value gaps, and more — step by step.
        </p>
        <div className={styles.actions}>
          <Link className={styles.primaryBtn} to="/tour">
            Start Tour 🚀
          </Link>
          <Link className={styles.secondaryBtn} to="/dashboard">
            View Dashboard
          </Link>
        </div>
      </div>

      <div className={styles.features}>
        <div className={styles.feature}>
          <span className={styles.icon}>🎓</span>
          <h3>7 Learning Stops</h3>
          <p>From Market Structure to Liquidity &amp; Inducement</p>
        </div>
        <div className={styles.feature}>
          <span className={styles.icon}>🤖</span>
          <h3>AI Trading Coach</h3>
          <p>Ask GPT-4 any trading question during the tour</p>
        </div>
        <div className={styles.feature}>
          <span className={styles.icon}>🗺️</span>
          <h3>Gap Map</h3>
          <p>Track completed and skipped stops at a glance</p>
        </div>
      </div>
    </main>
  );
}
