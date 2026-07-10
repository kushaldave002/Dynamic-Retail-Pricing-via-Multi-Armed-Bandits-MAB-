import math

import pytest

from mab.algorithms.base import make_policy


ALGORITHMS = ["epsilon_greedy", "ucb1", "sliding_window_ucb", "thompson_sampling"]


@pytest.mark.parametrize("name", ALGORITHMS)
def test_policy_selects_valid_arm(name):
    arms = [1.0, 2.0, 3.0]
    policy = make_policy(name, arms=arms, seed=7)

    selected = policy.select_arm()

    assert selected in arms


@pytest.mark.parametrize("name", ALGORITHMS)
def test_policy_updates_counts_and_values(name):
    arms = [1.0, 2.0, 3.0]
    policy = make_policy(name, arms=arms, seed=7)

    arm = policy.select_arm()
    policy.update(arm, 12.5)
    state = policy.state()

    assert state.total_pulls == 1
    assert state.counts[arm] == 1
    assert math.isclose(state.values[arm], 12.5)


def test_epsilon_greedy_exploits_best_observed_arm_when_epsilon_zero():
    policy = make_policy("epsilon_greedy", arms=[1.0, 2.0], seed=3, epsilon=0.0)
    policy.update(1.0, 5.0)
    policy.update(2.0, 9.0)

    assert policy.select_arm() == 2.0


def test_sliding_window_ucb_forgets_old_observations():
    policy = make_policy("sliding_window_ucb", arms=[1.0, 2.0], seed=3, window_size=2)
    policy.update(1.0, 100.0)
    policy.update(2.0, 1.0)
    policy.update(2.0, 1.0)

    state = policy.state()

    assert state.total_pulls == 2
    assert state.counts[1.0] == 0
    assert state.counts[2.0] == 2


def test_oracle_uses_environment_best_arm():
    policy = make_policy("oracle", arms=[1.0, 2.0], seed=1, best_arm=2.0)

    assert policy.select_arm() == 2.0

def test_oracle_rejects_best_arm_not_in_arms():
    with pytest.raises(ValueError, match="best_arm must be one of arms"):
        make_policy("oracle", arms=[1.0, 2.0], seed=1, best_arm=3.0)


def test_sliding_window_ucb_rejects_non_integral_window_size():
    with pytest.raises(ValueError, match="window_size must be an integer"):
        make_policy("sliding_window_ucb", arms=[1.0, 2.0], seed=3, window_size=2.5)


@pytest.mark.parametrize("epsilon", [-0.1, 1.5])
def test_epsilon_greedy_rejects_out_of_range_epsilon(epsilon):
    with pytest.raises(ValueError, match="epsilon must be between 0.0 and 1.0"):
        make_policy("epsilon_greedy", arms=[1.0, 2.0], seed=3, epsilon=epsilon)

