export type EnvironmentName = "empirical" | "elasticity";

export type AlgorithmName =
  | "epsilon_greedy"
  | "ucb1"
  | "sliding_window_ucb"
  | "thompson_sampling";

export type PriceRewardSeries = {
  arm: number;
  rewards: number[];
};

export type ElasticityModel = {
  base_price: number;
  base_demand: number;
  elasticity: number;
  noise_scale: number;
};

export type DatasetProduct = {
  id: string;
  name: string;
  observations: number;
  price_arms: number[];
  empirical_rewards?: PriceRewardSeries[];
  elasticity_model?: ElasticityModel;
  reward_row_count?: number;
  environment_source?: string;
};

export type DatasetCatalog = {
  source: string;
  products: DatasetProduct[];
};

export type ExperimentRequest = {
  environment: EnvironmentName;
  horizon: number;
  seed: number;
  algorithms: AlgorithmName[];
  parameters: Record<string, Record<string, number>>;
};

export type TraceRow = {
  environment: EnvironmentName;
  step: number;
  algorithm: string;
  arm: number;
  reward: number;
  cumulative_reward: number;
  cumulative_regret: number;
};

export type SummaryRow = {
  environment: EnvironmentName;
  algorithm: string;
  cumulative_reward: number;
  cumulative_regret: number;
  best_arm: number;
  pulls: number;
};

export type ExperimentResponse = {
  source: string;
  sample_product: DatasetProduct;
  summary: SummaryRow[];
  traces: TraceRow[];
};

export type PrecomputedOverview = {
  summaries: SummaryRow[];
  traces: TraceRow[];
};

export type LabDefaults = {
  environment: EnvironmentName;
  horizon: number;
  seed: number;
  algorithms: AlgorithmName[];
  epsilon: number;
  windowSize: number;
  sample_source: string;
};

export type PrecomputedResponse = {
  source: string;
  sample_product: DatasetProduct;
  overview: PrecomputedOverview;
  lab_defaults: LabDefaults;
};
