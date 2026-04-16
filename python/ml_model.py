"""XGBoost signal model.

Produces a directional signal: 1 (long), -1 (short), 0 (flat).

Features expected (in order)
-----------------------------
    rsi, atr, volume, price, spread, imbalance
"""

import os
import pickle
from typing import Optional

import numpy as np

try:
    import xgboost as xgb  # type: ignore
except ImportError:  # pragma: no cover
    xgb = None  # type: ignore

MODEL_PATH = os.getenv("XGBOOST_MODEL_PATH", "models/xgboost_model.pkl")
SIGNAL_THRESHOLD = float(os.getenv("XGBOOST_THRESHOLD", "0.5"))


class XGBoostModel:
    """Wrapper around a trained XGBoost classifier."""

    def __init__(self, model_path: str = MODEL_PATH) -> None:
        self.model_path = model_path
        self._model: Optional[object] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load a previously persisted model from disk."""
        with open(self.model_path, "rb") as fh:
            self._model = pickle.load(fh)

    def save(self) -> None:
        """Persist the current model to disk."""
        os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
        with open(self.model_path, "wb") as fh:
            pickle.dump(self._model, fh)

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit a fresh XGBoost classifier on labelled data."""
        if xgb is None:
            raise ImportError("xgboost is not installed")
        self._model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            use_label_encoder=False,
            eval_metric="logloss",
        )
        self._model.fit(X, y)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, features: dict) -> int:
        """Return a signal (-1, 0, 1) given a feature dict.

        Falls back to 0 (flat) when no model is loaded.
        """
        if self._model is None:
            return 0

        row = _extract_features(features)
        proba = self._model.predict_proba([row])[0]  # shape: (n_classes,)
        # Classes are assumed ordered: 0→short(-1), 1→flat(0), 2→long(1)
        class_idx = int(np.argmax(proba))
        if proba[class_idx] < SIGNAL_THRESHOLD:
            return 0
        return class_idx - 1  # map {0,1,2} → {-1,0,1}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_features(features: dict) -> list:
    return [
        float(features.get("rsi", 50)),
        float(features.get("atr", 0)),
        float(features.get("volume", 0)),
        float(features.get("price", 0)),
        float(features.get("spread", 0)),
        float(features.get("imbalance", 0)),
    ]
