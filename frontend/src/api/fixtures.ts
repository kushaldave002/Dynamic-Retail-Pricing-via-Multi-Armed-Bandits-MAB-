import type {
  DatasetCatalog,
  ExperimentRequest,
  ExperimentResponse,
  PrecomputedResponse,
} from "../types";

export const catalogFixture: DatasetCatalog = {
  source: "frontend_fixture",
  products: [
    {
      id: "FIX-001",
      name: "Trail Mug",
      observations: 120,
      price_arms: [18.0, 20.0, 22.0],
      empirical_rewards: [
        { arm: 18.0, rewards: [126, 144, 126, 144] },
        { arm: 20.0, rewards: [140, 160, 160, 140] },
        { arm: 22.0, rewards: [154, 176, 154, 132] }
      ],
      elasticity_model: {
        base_price: 20.0,
        base_demand: 8.2,
        elasticity: -1.1,
        noise_scale: 0.04,
      },
      environment_source: "frontend_fixture",
    },
  ],
};

export const precomputedFixture: PrecomputedResponse = {
  source: "frontend_fixture",
  sample_product: {
    id: "FIX-001",
    name: "Trail Mug",
    observations: 120,
    price_arms: [18.0, 20.0, 22.0],
    reward_row_count: 12,
    environment_source: "frontend_fixture",
  },
  overview: {
    summaries: [
      {
        environment: "elasticity",
        algorithm: "epsilon_greedy",
        cumulative_reward: 1492,
        cumulative_regret: 81,
        best_arm: 20.0,
        pulls: 5,
      },
      {
        environment: "elasticity",
        algorithm: "ucb1",
        cumulative_reward: 1586,
        cumulative_regret: 24,
        best_arm: 20.0,
        pulls: 5,
      },
    ],
    traces: [
      {
        environment: "elasticity",
        step: 1,
        algorithm: "epsilon_greedy",
        arm: 18.0,
        reward: 126,
        cumulative_reward: 126,
        cumulative_regret: 18,
      },
      {
        environment: "elasticity",
        step: 2,
        algorithm: "epsilon_greedy",
        arm: 20.0,
        reward: 160,
        cumulative_reward: 286,
        cumulative_regret: 18,
      },
      {
        environment: "elasticity",
        step: 3,
        algorithm: "epsilon_greedy",
        arm: 22.0,
        reward: 132,
        cumulative_reward: 418,
        cumulative_regret: 46,
      },
      {
        environment: "elasticity",
        step: 4,
        algorithm: "epsilon_greedy",
        arm: 20.0,
        reward: 160,
        cumulative_reward: 578,
        cumulative_regret: 46,
      },
      {
        environment: "elasticity",
        step: 5,
        algorithm: "epsilon_greedy",
        arm: 18.0,
        reward: 144,
        cumulative_reward: 722,
        cumulative_regret: 64,
      },
      {
        environment: "elasticity",
        step: 1,
        algorithm: "ucb1",
        arm: 20.0,
        reward: 160,
        cumulative_reward: 160,
        cumulative_regret: 0,
      },
      {
        environment: "elasticity",
        step: 2,
        algorithm: "ucb1",
        arm: 18.0,
        reward: 144,
        cumulative_reward: 304,
        cumulative_regret: 16,
      },
      {
        environment: "elasticity",
        step: 3,
        algorithm: "ucb1",
        arm: 20.0,
        reward: 160,
        cumulative_reward: 464,
        cumulative_regret: 16,
      },
      {
        environment: "elasticity",
        step: 4,
        algorithm: "ucb1",
        arm: 22.0,
        reward: 154,
        cumulative_reward: 618,
        cumulative_regret: 22,
      },
      {
        environment: "elasticity",
        step: 5,
        algorithm: "ucb1",
        arm: 20.0,
        reward: 160,
        cumulative_reward: 778,
        cumulative_regret: 22,
      }
    ],
  },
  lab_defaults: {
    environment: "elasticity",
    horizon: 200,
    seed: 42,
    algorithms: ["epsilon_greedy", "ucb1"],
    epsilon: 0.1,
    windowSize: 50,
    sample_source: "frontend_fixture",
  },
};

export function buildExperimentFixture(request: ExperimentRequest): ExperimentResponse {
  const filteredSummary = precomputedFixture.overview.summaries.filter(
    (row) =>
      row.environment === request.environment && request.algorithms.includes(row.algorithm as ExperimentRequest["algorithms"][number]),
  );
  const filteredTraces = precomputedFixture.overview.traces.filter(
    (row) =>
      row.environment === request.environment && request.algorithms.includes(row.algorithm as ExperimentRequest["algorithms"][number]),
  );

  return {
    source: "frontend_fixture",
    sample_product: precomputedFixture.sample_product,
    summary: filteredSummary.length > 0 ? filteredSummary : precomputedFixture.overview.summaries,
    traces: filteredTraces.length > 0 ? filteredTraces : precomputedFixture.overview.traces,
  };
}
