"""Model ensemble — combines XGBoost, Transformer, and RL Agent signals.

Voting strategy: simple majority vote.
  - +2 or +3  → long  ( 1)
  - -2 or -3  → short (-1)
  - anything else → flat (0)
"""

from ml_model import XGBoostModel
from transformer_model import TransformerModel
from rl_agent import RLAgent


def combine_models(
    xgb_model: XGBoostModel,
    transformer: TransformerModel,
    rl: RLAgent,
    features: dict,
    feature_window: list,
) -> int:
    """Return the ensemble signal (-1, 0, 1).

    Parameters
    ----------
    xgb_model:
        Loaded XGBoostModel instance.
    transformer:
        Loaded TransformerModel instance.
    rl:
        Loaded RLAgent instance.
    features:
        Single-step feature dict (rsi, atr, volume, price, spread, imbalance).
    feature_window:
        Sequence of feature dicts (most recent last) for the Transformer.
    """
    xgb_signal = xgb_model.predict(features)
    tf_signal = transformer.predict(feature_window)
    rl_signal = rl.predict(features)

    vote = xgb_signal + tf_signal + rl_signal

    if vote >= 2:
        return 1
    if vote <= -2:
        return -1
    return 0
