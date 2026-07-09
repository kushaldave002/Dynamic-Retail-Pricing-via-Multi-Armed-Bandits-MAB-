from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


AlgorithmName = Literal[
    "epsilon_greedy",
    "ucb1",
    "sliding_window_ucb",
    "thompson_sampling",
]
EnvironmentName = Literal["empirical", "elasticity"]


class SimulationRequest(BaseModel):
    environment: EnvironmentName
    horizon: int = Field(ge=10, le=1000)
    seed: int = Field(ge=0, le=1_000_000)
    algorithms: list[AlgorithmName]
    parameters: dict[str, dict[str, float | int]] = Field(default_factory=dict)


class TraceRowResponse(BaseModel):
    environment: EnvironmentName
    step: int
    algorithm: str
    arm: float
    reward: float
    cumulative_reward: float
    cumulative_regret: float


class SummaryRowResponse(BaseModel):
    environment: EnvironmentName
    algorithm: str
    cumulative_reward: float
    cumulative_regret: float
    best_arm: float
    pulls: int


class SimulationResponse(BaseModel):
    source: str
    sample_product: dict[str, object]
    summary: list[SummaryRowResponse]
    traces: list[TraceRowResponse]
