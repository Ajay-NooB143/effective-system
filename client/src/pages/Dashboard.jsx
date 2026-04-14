import { STOP_CATALOGUE } from "../services/tourData";
import styles from "./Dashboard.module.css";

export default function Dashboard() {
  return (
    <main className={styles.main}>
      <h1 className={styles.heading}>📊 Dashboard</h1>
      <p className={styles.sub}>
        All available tour stops and their descriptions.
      </p>

      <div className={styles.grid}>
        {STOP_CATALOGUE.map((stop, i) => (
          <div key={stop.name} className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={styles.num}>{i + 1}</span>
              <h3 className={styles.cardTitle}>{stop.title}</h3>
              {stop.levels !== "all" && (
                <span className={styles.levelTag}>{stop.levels}</span>
              )}
            </div>
            <p className={styles.cardContent}>{stop.content}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
