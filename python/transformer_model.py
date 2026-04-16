"""PyTorch Transformer signal model.

Consumes a sequence of feature vectors and outputs a directional signal:
  1 (long), -1 (short), 0 (flat).
"""

import os
from typing import Optional

import numpy as np

try:
    import torch
    import torch.nn as nn
except ImportError:  # pragma: no cover
    torch = None  # type: ignore
    nn = None  # type: ignore

MODEL_PATH = os.getenv("TRANSFORMER_MODEL_PATH", "models/transformer_model.pt")
SEQ_LEN = int(os.getenv("TRANSFORMER_SEQ_LEN", "10"))
D_MODEL = int(os.getenv("TRANSFORMER_D_MODEL", "32"))
N_HEADS = int(os.getenv("TRANSFORMER_N_HEADS", "4"))
N_LAYERS = int(os.getenv("TRANSFORMER_N_LAYERS", "2"))
N_FEATURES = 6  # rsi, atr, volume, price, spread, imbalance
N_CLASSES = 3  # short(-1), flat(0), long(1)
SIGNAL_THRESHOLD = float(os.getenv("TRANSFORMER_THRESHOLD", "0.5"))


class _TransformerNet(nn.Module if nn else object):
    """Encoder-only Transformer for sequence classification."""

    def __init__(self) -> None:
        super().__init__()
        self.input_proj = nn.Linear(N_FEATURES, D_MODEL)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL, nhead=N_HEADS, dim_feedforward=128, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=N_LAYERS)
        self.classifier = nn.Linear(D_MODEL, N_CLASSES)

    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        # x: (batch, seq_len, n_features)
        x = self.input_proj(x)
        x = self.encoder(x)
        x = x[:, -1, :]  # take last token
        return self.classifier(x)


class TransformerModel:
    """Wrapper around the Transformer network."""

    def __init__(self, model_path: str = MODEL_PATH) -> None:
        self.model_path = model_path
        self._net: Optional[object] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> None:
        if torch is None:
            raise ImportError("torch is not installed")
        net = _TransformerNet()
        net.load_state_dict(torch.load(self.model_path, map_location="cpu"))
        net.eval()
        self._net = net

    def save(self) -> None:
        if self._net is None or torch is None:
            return
        os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
        torch.save(self._net.state_dict(), self.model_path)

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 20) -> None:
        """Train from scratch on (N, SEQ_LEN, N_FEATURES) array X and labels y."""
        if torch is None:
            raise ImportError("torch is not installed")
        net = _TransformerNet()
        optimizer = torch.optim.Adam(net.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()

        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.long)

        net.train()
        for _ in range(epochs):
            optimizer.zero_grad()
            logits = net(X_t)
            loss = criterion(logits, y_t)
            loss.backward()
            optimizer.step()

        net.eval()
        self._net = net

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, feature_window: list) -> int:
        """Return a signal (-1, 0, 1).

        Parameters
        ----------
        feature_window:
            List of SEQ_LEN dicts, each with keys rsi/atr/volume/price/spread/imbalance.
            If fewer rows are provided the window is zero-padded on the left.
        """
        if self._net is None or torch is None:
            return 0

        seq = _build_sequence(feature_window)
        x = torch.tensor(seq, dtype=torch.float32).unsqueeze(0)  # (1, seq, feat)
        with torch.no_grad():
            logits = self._net(x)
            proba = torch.softmax(logits, dim=-1).squeeze().numpy()

        class_idx = int(np.argmax(proba))
        if proba[class_idx] < SIGNAL_THRESHOLD:
            return 0
        return class_idx - 1  # map {0,1,2} → {-1,0,1}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_vec(d: dict) -> list:
    return [
        float(d.get("rsi", 50)),
        float(d.get("atr", 0)),
        float(d.get("volume", 0)),
        float(d.get("price", 0)),
        float(d.get("spread", 0)),
        float(d.get("imbalance", 0)),
    ]


def _build_sequence(window: list) -> np.ndarray:
    rows = [_row_to_vec(d) for d in window[-SEQ_LEN:]]
    # Pad on the left with zeros if window is shorter than SEQ_LEN
    while len(rows) < SEQ_LEN:
        rows.insert(0, [0.0] * N_FEATURES)
    return np.array(rows, dtype=np.float32)
