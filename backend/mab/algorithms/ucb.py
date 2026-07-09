from __future__ import annotations

import math
import random
from collections import deque

from mab.algorithms.base import Arm, BanditState


class UCB1:
    name = "ucb1"

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

        def score(arm: Arm) -> float:
            return self._values[arm] + math.sqrt(2.0 * math.log(self._total_pulls) / self._counts[arm])

        return max(self.arms, key=score)

    def update(self, arm: Arm, reward: float) -> None:
        self._total_pulls += 1
        self._counts[arm] += 1
        count = self._counts[arm]
        current = self._values[arm]
        self._values[arm] = current + (reward - current) / count

    def state(self) -> BanditState:
        return BanditState(self.name, dict(self._counts), dict(self._values), self._total_pulls)


class SlidingWindowUCB:
    name = "sliding_window_ucb"

    def __init__(self, arms: list[Arm], seed: int = 0, window_size: int = 50, **_: object) -> None:
        if isinstance(window_size, bool):
            raise ValueError("window_size must be an integer")
        try:
            coerced_window_size = int(window_size)
        except (TypeError, ValueError) as exc:
            raise ValueError("window_size must be an integer") from exc
        if coerced_window_size != window_size:
            raise ValueError("window_size must be an integer")
        if coerced_window_size <= 0:
            raise ValueError("window_size must be positive")
        self.arms = list(arms)
        self._rng = random.Random(seed)
        self._window_size = coerced_window_size
        self._events: deque[tuple[Arm, float]] = deque()
        self._counts = {arm: 0 for arm in self.arms}
        self._values = {arm: 0.0 for arm in self.arms}
        self._total_pulls = 0

    def _recompute(self) -> None:
        self._counts = {arm: 0 for arm in self.arms}
        totals = {arm: 0.0 for arm in self.arms}
        for arm, reward in self._events:
            self._counts[arm] += 1
            totals[arm] += reward
        self._values = {
            arm: (totals[arm] / self._counts[arm]) if self._counts[arm] else 0.0
            for arm in self.arms
        }
        self._total_pulls = len(self._events)

    def select_arm(self) -> Arm:
        untried = [arm for arm in self.arms if self._counts[arm] == 0]
        if untried:
            return self._rng.choice(untried)

        def score(arm: Arm) -> float:
            return self._values[arm] + math.sqrt(2.0 * math.log(self._total_pulls) / self._counts[arm])

        return max(self.arms, key=score)

    def update(self, arm: Arm, reward: float) -> None:
        self._events.append((arm, reward))
        while len(self._events) > self._window_size:
            self._events.popleft()
        self._recompute()

    def state(self) -> BanditState:
        return BanditState(
            self.name,
            dict(self._counts),
            dict(self._values),
            self._total_pulls,
            {"window_size": float(self._window_size)},
        )

