import { useState } from "react";
import { buildStopList, inferLevel } from "../services/tourData";
import Survey from "../components/Survey";
import TourStep from "../components/TourStep";
import ChatBox from "../components/ChatBox";
import GapMap from "../components/GapMap";
import styles from "./Tour.module.css";

const PHASE = { SURVEY: "survey", TOURING: "touring", COMPLETE: "complete" };

export default function Tour() {
  const [phase, setPhase] = useState(PHASE.SURVEY);
  const [stops, setStops] = useState([]);
  const [stopIndex, setStopIndex] = useState(0);
  const [completed, setCompleted] = useState([]);
  const [level, setLevel] = useState("intermediate");

  function handleSurveyComplete(answers) {
    const detectedLevel = inferLevel(answers);
    const list = buildStopList(detectedLevel);
    setLevel(detectedLevel);
    setStops(list);
    setStopIndex(0);
    setCompleted([]);
    setPhase(PHASE.TOURING);
  }

  function handleNext() {
    const stop = stops[stopIndex];
    if (stop) {
      setCompleted((prev) => [...prev, stop.name]);
    }
    if (stopIndex + 1 >= stops.length) {
      setPhase(PHASE.COMPLETE);
    } else {
      setStopIndex((i) => i + 1);
    }
  }

  function handleRestart() {
    setPhase(PHASE.SURVEY);
    setStops([]);
    setStopIndex(0);
    setCompleted([]);
  }

  if (phase === PHASE.SURVEY) {
    return (
      <main className={styles.main}>
        <Survey onComplete={handleSurveyComplete} />
      </main>
    );
  }

  if (phase === PHASE.COMPLETE) {
    return (
      <main className={styles.main}>
        <div className={styles.complete}>
          <h2>🎉 Tour Complete!</h2>
          <p>
            You finished all {stops.length} stops. Great work! Review your gap
            map below to see which stops you completed.
          </p>
          <GapMap stops={stops} completed={completed} />
          <button className={styles.restartBtn} onClick={handleRestart}>
            Restart Tour
          </button>
        </div>
      </main>
    );
  }

  const currentStop = stops[stopIndex];

  return (
    <main className={styles.main}>
      <div className={styles.layout}>
        <div className={styles.left}>
          <p className={styles.levelBadge}>Level: {level}</p>
          <TourStep stop={currentStop} index={stopIndex} total={stops.length} />
          <button className={styles.nextBtn} onClick={handleNext}>
            {stopIndex + 1 < stops.length ? "Next Stop →" : "Finish Tour 🎉"}
          </button>
          <ChatBox context={currentStop?.title} />
        </div>
        <div className={styles.right}>
          <GapMap stops={stops} completed={completed} />
        </div>
      </div>
    </main>
  );
}
