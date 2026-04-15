"""Custom Gym trading environment used by the PPO agent.

Observation space : [rsi, atr, volume, price, spread, imbalance, position]
Action space      : Discrete(3)  →  0=short, 1=flat, 2=long
"""

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:  # pragma: no cover
    try:
        import gym  # type: ignore
        from gym import spaces  # type: ignore
    except ImportError:
        gym = None  # type: ignore
        spaces = None  # type: ignore

N_FEATURES = 7  # 6 market + 1 position


class TradingEnv(gym.Env if gym else object):
    """Episode-based simulation environment for training / evaluating RL agents.

    Parameters
    ----------
    data:
        List of dicts, each containing keys rsi/atr/volume/price/spread/imbalance.
    initial_balance:
        Starting portfolio value in quote currency.
    """

    metadata = {"render_modes": []}

    def __init__(self, data: list, initial_balance: float = 10_000.0) -> None:
        super().__init__()
        self.data = data
        self.initial_balance = initial_balance

        if spaces is not None:
            self.observation_space = spaces.Box(
                low=-np.inf, high=np.inf, shape=(N_FEATURES,), dtype=np.float32
            )
            self.action_space = spaces.Discrete(3)

        self._reset_state()

    # ------------------------------------------------------------------
    # Gym interface
    # ------------------------------------------------------------------

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed) if hasattr(super(), "reset") else None
        self._reset_state()
        obs = self._obs()
        return obs, {}

    def step(self, action: int):
        prev_value = self._portfolio_value()

        # Map action → position (-1, 0, 1)
        self._position = action - 1

        self._step += 1
        done = self._step >= len(self.data) - 1

        cur_price = float(self.data[self._step].get("price", 1))
        prev_price = float(self.data[self._step - 1].get("price", 1))
        pct_change = (cur_price - prev_price) / (prev_price + 1e-9)
        self._balance += self._balance * self._position * pct_change

        reward = self._portfolio_value() - prev_value
        obs = self._obs()
        return obs, float(reward), done, False, {}

    def render(self):
        pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _reset_state(self) -> None:
        self._step = 0
        self._position = 0
        self._balance = self.initial_balance

    def _portfolio_value(self) -> float:
        return self._balance

    def _obs(self) -> np.ndarray:
        row = self.data[min(self._step, len(self.data) - 1)]
        return np.array(
            [
                float(row.get("rsi", 50)),
                float(row.get("atr", 0)),
                float(row.get("volume", 0)),
                float(row.get("price", 0)),
                float(row.get("spread", 0)),
                float(row.get("imbalance", 0)),
                float(self._position),
            ],
            dtype=np.float32,
        )
