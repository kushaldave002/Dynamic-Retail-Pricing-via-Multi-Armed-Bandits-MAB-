from __future__ import annotations

from mab.algorithms.base import Arm, BanditState


class OraclePolicy:
    name = "oracle"

    def __init__(self, arms: list[Arm], seed: int = 0, best_arm: Arm | None = None, **_: object) -> None:
        if best_arm is None:
            raise ValueError("best_arm is required")
        self.arms = list(arms)
        self.best_arm = best_arm
        self._counts = {arm: 0 for arm in self.arms}
        self._values = {arm: 0.0 for arm in self.arms}
        self._total_pulls = 0

    def select_arm(self) -> Arm:
        return self.best_arm

    def update(self, arm: Arm, reward: float) -> None:
        self._total_pulls += 1
        self._counts[arm] += 1
        count = self._counts[arm]
        current = self._values[arm]
        self._values[arm] = current + (reward - current) / count

    def state(self) -> BanditState:
        return BanditState(self.name, dict(self._counts), dict(self._values), self._total_pulls)
