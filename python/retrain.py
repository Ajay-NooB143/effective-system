"""Weekly model retrain scheduler.

Run as a long-lived process alongside the Flask app:

    python retrain.py

It calls ``retrain_all()`` immediately on startup, then once every 7 days.
Data for retraining must be supplied by the application via the shared
``RETRAIN_DATA`` list (populated by the webhook handler).
"""

import logging
import os
import time
from typing import List

try:
    import schedule  # type: ignore
except ImportError:
    schedule = None  # type: ignore

import numpy as np

from ml_model import XGBoostModel
from transformer_model import TransformerModel
from rl_agent import RLAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

RETRAIN_INTERVAL_DAYS = int(os.getenv("RETRAIN_INTERVAL_DAYS", "7"))

# Shared buffer — the webhook appends labelled rows here
RETRAIN_DATA: List[dict] = []


def retrain_all(data: list = None) -> None:
    """Retrain XGBoost, Transformer, and RL Agent on the provided data.

    Parameters
    ----------
    data:
        List of labelled dicts:
        ``{rsi, atr, volume, price, spread, imbalance, label}``.
        Labels must be in {-1, 0, 1} (short / flat / long).
        Falls back to the module-level ``RETRAIN_DATA`` buffer when omitted.
    """
    rows = data if data is not None else RETRAIN_DATA
    if not rows:
        logger.warning("Retrain skipped — no data available")
        return

    # Convert to numpy arrays for XGBoost / Transformer
    X = np.array(
        [
            [
                float(r.get("rsi", 50)),
                float(r.get("atr", 0)),
                float(r.get("volume", 0)),
                float(r.get("price", 0)),
                float(r.get("spread", 0)),
                float(r.get("imbalance", 0)),
            ]
            for r in rows
        ],
        dtype=np.float32,
    )
    y = np.array([int(r.get("label", 0)) + 1 for r in rows], dtype=np.int64)
    # Labels remapped: {-1→0, 0→1, 1→2}

    logger.info("Retraining XGBoost on %d samples …", len(rows))
    xgb = XGBoostModel()
    xgb.train(X, y)
    xgb.save()
    logger.info("XGBoost retrained and saved → %s", xgb.model_path)

    # Build windowed sequences for the Transformer
    seq_len = 10
    if len(rows) >= seq_len:
        X_seq = np.array(
            [X[i : i + seq_len] for i in range(len(rows) - seq_len)],
            dtype=np.float32,
        )
        y_seq = y[seq_len:]
        logger.info("Retraining Transformer on %d sequences …", len(X_seq))
        tf = TransformerModel()
        tf.train(X_seq, y_seq)
        tf.save()
        logger.info("Transformer retrained and saved → %s", tf.model_path)
    else:
        logger.warning(
            "Transformer retrain skipped — need at least %d rows, got %d",
            seq_len,
            len(rows),
        )

    logger.info("Retraining RL Agent (Q-Table) on %d episodes …", len(rows))
    rl = RLAgent()
    rl.train_qtable(rows, episodes=50)
    rl.save_qtable()
    logger.info("RL Agent retrained and saved → %s", rl._qtable is not None)

    try:
        logger.info("Retraining PPO agent …")
        rl.train_ppo(rows, total_timesteps=10_000)
        rl.save_ppo()
        logger.info("PPO agent retrained and saved")
    except ImportError:
        logger.warning("stable-baselines3 not available — PPO retrain skipped")


def _schedule_loop() -> None:
    if schedule is None:
        raise ImportError(
            "schedule is not installed. Run: pip install schedule"
        )

    schedule.every(RETRAIN_INTERVAL_DAYS).days.do(retrain_all)
    logger.info(
        "Retrain scheduler started — will run every %d day(s)", RETRAIN_INTERVAL_DAYS
    )

    # Run immediately on startup
    retrain_all()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    _schedule_loop()
