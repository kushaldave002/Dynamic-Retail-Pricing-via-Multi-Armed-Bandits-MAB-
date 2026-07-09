from __future__ import annotations

import random


class ElasticityEnvironment:
    def __init__(
        self,
        *,
        base_price: float,
        base_demand: float,
        elasticity: float,
        arms: list[float],
        seed: int = 0,
        noise_scale: float = 0.1,
    ) -> None:
        if not arms:
            raise ValueError("arms must contain at least one price")

        self.base_price = float(base_price)
        self.base_demand = float(base_demand)
        self.elasticity = float(elasticity)
        self.arms = [float(arm) for arm in arms]
        self.noise_scale = float(noise_scale)
        self._rng = random.Random(seed)

    def pull(self, arm: float) -> float:
        expected_reward = self.expected_reward(arm)
        reward = self._rng.gauss(expected_reward, expected_reward * self.noise_scale)
        return max(0.0, reward)

    def expected_reward(self, arm: float) -> float:
        checked_arm = self._validate_arm(arm)
        expected_demand = max(
            0.0,
            self.base_demand * (checked_arm / self.base_price) ** self.elasticity,
        )
        return checked_arm * expected_demand

    def best_arm(self) -> float:
        return max(self.arms, key=self.expected_reward)

    def _validate_arm(self, arm: float) -> float:
        checked_arm = float(arm)
        if checked_arm not in self.arms:
            raise ValueError(f"unknown arm: {arm}")
        return checked_arm
