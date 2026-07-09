from mab.environments.elasticity import ElasticityEnvironment
from mab.environments.empirical import EmpiricalArmEnvironment


def test_empirical_environment_samples_known_rewards():
    env = EmpiricalArmEnvironment(rewards_by_arm={1.0: [10.0, 12.0], 2.0: [8.0]}, seed=1)

    reward = env.pull(1.0)

    assert reward in {10.0, 12.0}
    assert env.best_arm() == 1.0


def test_elasticity_environment_rewards_peak_near_reasonable_price():
    env = ElasticityEnvironment(
        base_price=10.0,
        base_demand=20.0,
        elasticity=-1.2,
        arms=[8.0, 10.0, 12.0],
        seed=4,
        noise_scale=0.0,
    )

    rewards = {arm: env.expected_reward(arm) for arm in env.arms}

    assert rewards[12.0] > 0
    assert env.best_arm() in env.arms


def test_elasticity_environment_best_arm_expected_reward_beats_each_arm():
    env = ElasticityEnvironment(
        base_price=10.0,
        base_demand=20.0,
        elasticity=-1.2,
        arms=[8.0, 10.0, 12.0],
        seed=4,
        noise_scale=0.0,
    )

    best_reward = env.expected_reward(env.best_arm())

    assert all(best_reward >= env.expected_reward(arm) for arm in env.arms)
