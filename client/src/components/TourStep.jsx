import styles from "./TourStep.module.css";

export default function TourStep({ stop, index, total }) {
  if (!stop) return null;

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.badge}>
          Stop {index + 1} / {total}
        </span>
        <h2 className={styles.title}>{stop.title}</h2>
      </div>

      <p className={styles.content}>{stop.content}</p>

      <div className={styles.factCheck}>
        <h3>📋 Fact Check</h3>
        {stop.fact_labels.map(([claim, label], i) => (
          <div key={i} className={styles.fact}>
            <span className={styles.label}>{label}</span>
            <span className={styles.claim}>{claim}</span>
          </div>
        ))}
      </div>

      <div className={styles.demo}>
        <h3>🎯 Exercise</h3>
        <p>{stop.demo_prompt}</p>
      </div>
    </div>
  );
}
