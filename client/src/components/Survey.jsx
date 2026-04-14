import { useState } from "react";
import styles from "./Survey.module.css";

const QUESTIONS = [
  "How long have you been studying or trading markets? (e.g. 'never traded', '6 months', '3 years as a prop trader')",
  "Which concept feels most confusing right now? (e.g. 'market structure', 'entries', 'risk sizing', 'all of it')",
  "What is your primary goal for this tour? (e.g. 'understand the codebase', 'learn trading basics', 'both')",
];

export default function Survey({ onComplete }) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [current, setCurrent] = useState("");

  const progress = Math.round((step / QUESTIONS.length) * 100);

  function handleSubmit(e) {
    e.preventDefault();
    const answer = current.trim() || "skip";
    const next = [...answers, answer];
    setAnswers(next);
    setCurrent("");

    if (step + 1 >= QUESTIONS.length) {
      onComplete(next);
    } else {
      setStep(step + 1);
    }
  }

  return (
    <div className={styles.wrapper}>
      <h2 className={styles.heading}>📝 Personalise Your Tour</h2>
      <p className={styles.sub}>
        Question {step + 1} of {QUESTIONS.length}
      </p>

      <div className={styles.progressBar}>
        <div className={styles.progressFill} style={{ width: `${progress}%` }} />
      </div>

      <form onSubmit={handleSubmit} className={styles.form}>
        <label className={styles.question}>{QUESTIONS[step]}</label>
        <input
          className={styles.input}
          type="text"
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          placeholder="Your answer (or leave blank to skip)"
          autoFocus
        />
        <button className={styles.btn} type="submit">
          {step + 1 < QUESTIONS.length ? "Next →" : "Start Tour 🚀"}
        </button>
      </form>
    </div>
  );
}
