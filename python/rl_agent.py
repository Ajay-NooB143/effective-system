"""Reinforcement-learning agent: Q-Table for live inference + PPO (SB3) for training.

The Q-Table discretises the observation space and is used during live trading
for fast, zero-dependency inference.  The PPO agent (Stable-Baselines3) is
used for offline training and periodically transfers its learned policy into
the Q-Table.
"""

import os
import pickle
from typing import Optional

import numpy as np

try:
    from stable_baselines3 import PPO  # type: ignore
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False

from trading_env import TradingEnv

QTABLE_PATH = os.getenv("QTABLE_PATH", "models/qtable.pkl")
PPO_PATH = os.getenv("PPO_MODEL_PATH", "models/ppo_model")

# Q-Table hyper-parameters
N_ACTIONS = 3       # 0=short, 1=flat, 2=long
N_BINS = 10         # bins per feature dimension
N_FEATURES = 7      # must match TradingEnv observation space
ALPHA = 0.1         # learning rate
GAMMA = 0.99        # discount factor
EPSILON_INIT = 0.3  # ε-greedy exploration (decays over time)


class RLAgent:
    """Hybrid Q-Table / PPO agent."""

    def __init__(self) -> None:
        # Q-Table: shape (N_BINS,)*N_FEATURES x N_ACTIONS
        self._qtable: Optional[np.ndarray] = None
        self._epsilon: float = EPSILON_INIT
        self._ppo: Optional[object] = None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load_qtable(self, path: str = QTABLE_PATH) -> None:
        with open(path, "rb") as fh:
            self._qtable = pickle.load(fh)

    def save_qtable(self, path: str = QTABLE_PATH) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as fh:
            pickle.dump(self._qtable, fh)

    def load_ppo(self, path: str = PPO_PATH) -> None:
        if not SB3_AVAILABLE:
            raise ImportError("stable-baselines3 is not installed")
        self._ppo = PPO.load(path)

    def save_ppo(self, path: str = PPO_PATH) -> None:
        if self._ppo is None:
            return
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._ppo.save(path)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train_ppo(self, data: list, total_timesteps: int = 50_000) -> None:
        """Train the PPO agent on historical data."""
        if not SB3_AVAILABLE:
            raise ImportError("stable-baselines3 is not installed")

        env = TradingEnv(data)
        self._ppo = PPO("MlpPolicy", env, verbose=0)
        self._ppo.learn(total_timesteps=total_timesteps)

    def train_qtable(
        self, data: list, episodes: int = 100, bins: Optional[list] = None
    ) -> None:
        """Train Q-Table via tabular Q-learning on historical data."""
        shape = tuple([N_BINS] * N_FEATURES) + (N_ACTIONS,)
        q = np.zeros(shape)

        env = TradingEnv(data)
        obs_bins = bins or _default_bins()

        for _ in range(episodes):
            obs, _ = env.reset()
            done = False
            while not done:
                state = _discretise(obs, obs_bins)
                if np.random.random() < self._epsilon:
                    action = np.random.randint(N_ACTIONS)
                else:
                    action = int(np.argmax(q[state]))

                next_obs, reward, done, _, _ = env.step(action)
                next_state = _discretise(next_obs, obs_bins)

                best_next = float(np.max(q[next_state]))
                q[state][action] += ALPHA * (
                    reward + GAMMA * best_next - q[state][action]
                )
                obs = next_obs

        self._qtable = q
        self._epsilon = max(0.05, self._epsilon * 0.95)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, features: dict) -> int:
        """Return action (-1, 0, 1) for the given feature dict.

        Prefers Q-Table for low-latency live inference; falls back to PPO
        when the Q-Table is unavailable.
        """
        obs = _features_to_obs(features)

        if self._qtable is not None:
            bins = _default_bins()
            state = _discretise(obs, bins)
            action = int(np.argmax(self._qtable[state]))
            return action - 1  # map {0,1,2} → {-1,0,1}

        if self._ppo is not None:
            action, _ = self._ppo.predict(obs, deterministic=True)
            return int(action) - 1

        return 0  # flat when nothing is loaded

    def update(self, features: dict, action: int, reward: float, next_features: dict) -> None:
        """Online Q-Table update from a completed step (reward feedback loop)."""
        if self._qtable is None:
            return

        bins = _default_bins()
        obs = _features_to_obs(features)
        next_obs = _features_to_obs(next_features)

        state = _discretise(obs, bins)
        next_state = _discretise(next_obs, bins)

        a_idx = action + 1  # map {-1,0,1} → {0,1,2}
        best_next = float(np.max(self._qtable[next_state]))
        self._qtable[state][a_idx] += ALPHA * (
            reward + GAMMA * best_next - self._qtable[state][a_idx]
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _features_to_obs(features: dict) -> np.ndarray:
    return np.array(
        [
            float(features.get("rsi", 50)),
            float(features.get("atr", 0)),
            float(features.get("volume", 0)),
            float(features.get("price", 0)),
            float(features.get("spread", 0)),
            float(features.get("imbalance", 0)),
            float(features.get("position", 0)),
        ],
        dtype=np.float32,
    )


def _default_bins() -> list:
    """Return per-feature bin edges used to discretise the observation space."""
    return [
        np.linspace(0, 100, N_BINS + 1),      # rsi
        np.linspace(0, 1000, N_BINS + 1),     # atr
        np.linspace(0, 1e9, N_BINS + 1),      # volume
        np.linspace(0, 1e6, N_BINS + 1),      # price
        np.linspace(0, 100, N_BINS + 1),      # spread
        np.linspace(-1, 1, N_BINS + 1),       # imbalance
        np.linspace(-1, 1, N_BINS + 1),       # position
    ]


def _discretise(obs: np.ndarray, bins: list) -> tuple:
    return tuple(
        int(np.clip(np.digitize(obs[i], bins[i]) - 1, 0, N_BINS - 1))
        for i in range(len(bins))
    )
