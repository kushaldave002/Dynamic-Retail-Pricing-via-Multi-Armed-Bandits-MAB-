from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

Arm = float


@dataclass(frozen=True)
class BanditState:
    name: str
    counts: dict[Arm, int]
    values: dict[Arm, float]
    total_pulls: int
    metadata: dict[str, float] = field(default_factory=dict)


class BanditPolicy(Protocol):
    name: str
    arms: list[Arm]

    def select_arm(self) -> Arm:
        ...

    def update(self, arm: Arm, reward: float) -> None:
        ...

    def state(self) -> BanditState:
        ...


def make_policy(name: str, arms: list[Arm], seed: int = 0, **params: object) -> BanditPolicy:
    if not arms:
        raise ValueError("arms must contain at least one price")

    from mab.algorithms.epsilon_greedy import EpsilonGreedy
    from mab.algorithms.oracle import OraclePolicy
    from mab.algorithms.thompson import ThompsonSampling
    from mab.algorithms.ucb import SlidingWindowUCB, UCB1

    registry = {
        "epsilon_greedy": EpsilonGreedy,
        "ucb1": UCB1,
        "sliding_window_ucb": SlidingWindowUCB,
        "thompson_sampling": ThompsonSampling,
        "oracle": OraclePolicy,
    }
    try:
        policy_cls = registry[name]
    except KeyError as exc:
        raise ValueError(f"unsupported algorithm: {name}") from exc
    return policy_cls(arms=arms, seed=seed, **params)
