from __future__ import annotations

from typing import Protocol


class PricingEnvironment(Protocol):
    arms: list[float]

    def pull(self, arm: float) -> float:
        ...

    def expected_reward(self, arm: float) -> float:
        ...

    def best_arm(self) -> float:
        ...
