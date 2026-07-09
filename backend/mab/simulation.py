from __future__ import annotations

import copy
from dataclasses import dataclass

from mab.algorithms.base import make_policy
from mab.environments.base import PricingEnvironment
from mab.metrics import SummaryRow, TraceRow


@dataclass(frozen=True)
class SimulationRequestConfig:
    algorithms: list[str]
    horizon: int
    seed: int = 0
    parameters: dict[str, dict[str, object]] | None = None


@dataclass(frozen=True)
class SimulationResult:
    traces: list[TraceRow]
    summary: list[SummaryRow]
    arms: list[float]


def run_simulation(
    *,
    environment: PricingEnvironment,
    algorithms: list[str],
    horizon: int,
    seed: int = 0,
    parameters: dict[str, dict[str, object]] | None = None,
) -> SimulationResult:
    if horizon <= 0:
        raise ValueError("horizon must be positive")
    if not algorithms:
        raise ValueError("algorithms must contain at least one policy")

    config = SimulationRequestConfig(
        algorithms=list(algorithms),
        horizon=horizon,
        seed=seed,
        parameters=parameters,
    )
    best_arm = environment.best_arm()
    oracle_reward = environment.expected_reward(best_arm)
    traces: list[TraceRow] = []
    summary: list[SummaryRow] = []

    for index, algorithm in enumerate(config.algorithms):
        policy_params = dict((config.parameters or {}).get(algorithm, {}))
        if algorithm == "oracle" and "best_arm" not in policy_params:
            policy_params["best_arm"] = best_arm
        policy = make_policy(
            algorithm,
            arms=list(environment.arms),
            seed=config.seed + index,
            **policy_params,
        )
        policy_environment = copy.deepcopy(environment)
        cumulative_reward = 0.0
        cumulative_regret = 0.0

        for step in range(1, config.horizon + 1):
            arm = float(policy.select_arm())
            reward = float(policy_environment.pull(arm))
            policy.update(arm, reward)
            cumulative_reward += reward
            cumulative_regret += oracle_reward - policy_environment.expected_reward(arm)
            traces.append(
                TraceRow(
                    step=step,
                    algorithm=algorithm,
                    arm=arm,
                    reward=reward,
                    cumulative_reward=cumulative_reward,
                    cumulative_regret=cumulative_regret,
                )
            )

        summary.append(
            SummaryRow(
                algorithm=algorithm,
                cumulative_reward=cumulative_reward,
                cumulative_regret=cumulative_regret,
                best_arm=best_arm,
                pulls=config.horizon,
            )
        )

    return SimulationResult(traces=traces, summary=summary, arms=list(environment.arms))
