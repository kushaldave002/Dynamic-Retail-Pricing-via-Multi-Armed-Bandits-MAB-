from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TraceRow:
    step: int
    algorithm: str
    arm: float
    reward: float
    cumulative_reward: float
    cumulative_regret: float


@dataclass(frozen=True)
class SummaryRow:
    algorithm: str
    cumulative_reward: float
    cumulative_regret: float
    best_arm: float
    pulls: int
