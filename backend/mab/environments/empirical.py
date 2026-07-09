from __future__ import annotations

import random


class EmpiricalArmEnvironment:
    def __init__(self, rewards_by_arm: dict[float, list[float]], seed: int = 0) -> None:
        if not rewards_by_arm:
            raise ValueError("rewards_by_arm must contain at least one arm")

        normalized: dict[float, list[float]] = {}
        for arm, rewards in rewards_by_arm.items():
            if not rewards:
                raise ValueError("each arm must have at least one reward")
            normalized[float(arm)] = [float(reward) for reward in rewards]

        self.arms = list(normalized)
        self._rewards_by_arm = normalized
        self._rng = random.Random(seed)

    def pull(self, arm: float) -> float:
        rewards = self._rewards_for_arm(arm)
        return self._rng.choice(rewards)

    def expected_reward(self, arm: float) -> float:
        rewards = self._rewards_for_arm(arm)
        return sum(rewards) / len(rewards)

    def best_arm(self) -> float:
        return max(self.arms, key=self.expected_reward)

    def _rewards_for_arm(self, arm: float) -> list[float]:
        try:
            return self._rewards_by_arm[float(arm)]
        except KeyError as exc:
            raise ValueError(f"unknown arm: {arm}") from exc
