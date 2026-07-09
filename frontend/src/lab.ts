import type { AlgorithmName, EnvironmentName, ExperimentRequest } from "./types";

export const LAB_HORIZON_MIN = 10;
export const LAB_HORIZON_MAX = 1000;
export const LAB_EPSILON_MIN = 0.01;
export const LAB_EPSILON_MAX = 0.5;
export const LAB_WINDOW_MIN = 1;

export type LabSettings = {
  environment: EnvironmentName;
  horizon: number;
  seed: number;
  algorithms: AlgorithmName[];
  epsilon: number;
  windowSize: number;
};

export const DEFAULT_LAB_SETTINGS: LabSettings = {
  environment: "elasticity",
  horizon: 200,
  seed: 42,
  algorithms: ["epsilon_greedy", "ucb1", "sliding_window_ucb", "thompson_sampling"],
  epsilon: 0.1,
  windowSize: 50,
};

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function normalizeInteger(value: number, fallback: number, min?: number, max?: number) {
  if (!Number.isFinite(value)) {
    return fallback;
  }

  const rounded = Math.round(value);

  if (min === undefined || max === undefined) {
    return rounded;
  }

  return clamp(rounded, min, max);
}

export function normalizeLabSettings(settings: LabSettings): LabSettings {
  return {
    environment: settings.environment,
    horizon: normalizeInteger(
      settings.horizon,
      DEFAULT_LAB_SETTINGS.horizon,
      LAB_HORIZON_MIN,
      LAB_HORIZON_MAX,
    ),
    seed: normalizeInteger(settings.seed, DEFAULT_LAB_SETTINGS.seed),
    algorithms: Array.from(new Set(settings.algorithms)),
    epsilon: Number(clamp(settings.epsilon, LAB_EPSILON_MIN, LAB_EPSILON_MAX).toFixed(2)),
    windowSize: normalizeInteger(
      settings.windowSize,
      DEFAULT_LAB_SETTINGS.windowSize,
      LAB_WINDOW_MIN,
      Number.MAX_SAFE_INTEGER,
    ),
  };
}

export function buildExperimentRequest(settings: LabSettings): ExperimentRequest {
  const normalized = normalizeLabSettings(settings);

  return {
    environment: normalized.environment,
    horizon: normalized.horizon,
    seed: normalized.seed,
    algorithms: normalized.algorithms,
    parameters: {
      epsilon_greedy: { epsilon: normalized.epsilon },
      sliding_window_ucb: { window_size: normalized.windowSize },
      ucb1: {},
      thompson_sampling: {},
    },
  };
}

export function formatAlgorithmName(algorithm: string) {
  return algorithm
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

export function areLabSettingsEqual(left: LabSettings, right: LabSettings) {
  return (
    left.environment === right.environment &&
    left.horizon === right.horizon &&
    left.seed === right.seed &&
    left.epsilon === right.epsilon &&
    left.windowSize === right.windowSize &&
    left.algorithms.length === right.algorithms.length &&
    left.algorithms.every((algorithm, index) => algorithm === right.algorithms[index])
  );
}
