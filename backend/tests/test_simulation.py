from mab.environments.empirical import EmpiricalArmEnvironment
from mab.simulation import run_simulation


def test_run_simulation_returns_trace_and_summary():
    env = EmpiricalArmEnvironment({1.0: [5.0], 2.0: [10.0]}, seed=2)

    result = run_simulation(
        environment=env,
        algorithms=["epsilon_greedy", "ucb1"],
        horizon=8,
        seed=9,
        parameters={"epsilon_greedy": {"epsilon": 0.1}},
    )

    assert len(result.traces) == 16
    assert {row.algorithm for row in result.summary} == {"epsilon_greedy", "ucb1"}
    assert all(row.cumulative_regret >= 0 for row in result.summary)


def test_run_simulation_is_deterministic_for_same_seed():
    first = run_simulation(
        environment=EmpiricalArmEnvironment({1.0: [5.0, 7.0], 2.0: [10.0, 12.0]}, seed=2),
        algorithms=["epsilon_greedy", "ucb1"],
        horizon=8,
        seed=9,
        parameters={"epsilon_greedy": {"epsilon": 0.1}},
    )
    second = run_simulation(
        environment=EmpiricalArmEnvironment({1.0: [5.0, 7.0], 2.0: [10.0, 12.0]}, seed=2),
        algorithms=["epsilon_greedy", "ucb1"],
        horizon=8,
        seed=9,
        parameters={"epsilon_greedy": {"epsilon": 0.1}},
    )

    assert first == second


def test_run_simulation_supports_oracle_algorithm_and_zero_regret():
    env = EmpiricalArmEnvironment({1.0: [3.0], 2.0: [5.0]}, seed=4)

    result = run_simulation(
        environment=env,
        algorithms=["oracle"],
        horizon=6,
        seed=11,
    )

    assert len(result.traces) == 6
    assert result.summary[0].algorithm == "oracle"
    assert result.summary[0].best_arm == 2.0
    assert result.summary[0].cumulative_regret == 0.0
    assert all(row.arm == 2.0 for row in result.traces)
    assert all(row.cumulative_regret == 0.0 for row in result.traces)