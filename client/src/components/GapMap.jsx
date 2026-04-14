import styles from "./GapMap.module.css";

export default function GapMap({ stops, completed }) {
  return (
    <div className={styles.wrapper}>
      <h3 className={styles.heading}>🗺️ Gap Map</h3>
      <ul className={styles.list}>
        {stops.map((stop) => {
          const done = completed.includes(stop.name);
          return (
            <li key={stop.name} className={done ? styles.done : styles.pending}>
              <span className={styles.icon}>{done ? "✅" : "⬜"}</span>
              <span>{stop.title}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
