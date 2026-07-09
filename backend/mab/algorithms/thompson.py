from __future__ import annotations

import math
import random

from mab.algorithms.base import Arm, BanditState


class ThompsonSampling:
    name = "thompson_sampling"

    def __init__(self, arms: list[Arm], seed: int = 0, **_: object) -> None:
        self.arms = list(arms)
        self._rng = random.Random(seed)
        self._counts = {arm: 0 for arm in self.arms}
        self._values = {arm: 0.0 for arm in self.arms}
        self._total_pulls = 0

    def select_arm(self) -> Arm:
        untried = [arm for arm in self.arms if self._counts[arm] == 0]
        if untried:
            return self._rng.choice(untried)

        def sample(arm: Arm) -> float:
            scale = 1.0 / math.sqrt(self._counts[arm])
            return self._rng.gauss(self._values[arm], scale)

        return max(self.arms, key=sample)

    def update(self, arm: Arm, reward: float) -> None:
        self._total_pulls += 1
        self._counts[arm] += 1
        count = self._counts[arm]
        current = self._values[arm]
        self._values[arm] = current + (reward - current) / count

    def state(self) -> BanditState:
        return BanditState(self.name, dict(self._counts), dict(self._values), self._total_pulls)
