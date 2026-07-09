import type { AlgorithmName, EnvironmentName } from "../types";

export type LabSettings = {
  environment: EnvironmentName;
  horizon: number;
  seed: number;
  algorithms: AlgorithmName[];
  epsilon: number;
  windowSize: number;
};

type LabControlsProps = {
  settings: LabSettings;
  onChange: (settings: LabSettings) => void;
  onRun: () => void;
  isRunning: boolean;
};

const ALGORITHM_OPTIONS: Array<{ value: AlgorithmName; label: string; detail: string }> = [
  { value: "epsilon_greedy", label: "Epsilon-Greedy", detail: "Simple explore/exploit baseline" },
  { value: "ucb1", label: "UCB1", detail: "Confidence-bound exploration" },
  {
    value: "sliding_window_ucb",
    label: "Sliding Window UCB",
    detail: "Recent-history adaptation",
  },
  {
    value: "thompson_sampling",
    label: "Thompson Sampling",
    detail: "Posterior-driven exploration",
  },
];

function updateNumber(
  settings: LabSettings,
  key: "horizon" | "seed" | "windowSize",
  value: string,
): LabSettings {
  const parsed = Number(value);

  return {
    ...settings,
    [key]: Number.isFinite(parsed) ? parsed : 0,
  };
}

export function LabControls({ settings, onChange, onRun, isRunning }: LabControlsProps) {
  const isRunDisabled = isRunning || settings.algorithms.length === 0 || settings.horizon <= 0;

  return (
    <section className="dashboard-panel lab-controls-panel" aria-label="Lab controls">
      <div className="panel-topline">
        <div>
          <p className="panel-kicker">Simulation controls</p>
          <h2>Configure a live experiment run</h2>
        </div>
      </div>

      <div className="lab-controls-grid">
        <fieldset className="control-group">
          <legend>Environment</legend>
          <div className="segmented-control" role="radiogroup" aria-label="Environment">
            {(["empirical", "elasticity"] as const).map((environment) => (
              <button
                key={environment}
                type="button"
                role="radio"
                aria-checked={settings.environment === environment}
                className={
                  settings.environment === environment ? "segment is-active" : "segment"
                }
                onClick={() => onChange({ ...settings, environment })}
              >
                {environment === "empirical" ? "Empirical" : "Elasticity"}
              </button>
            ))}
          </div>
        </fieldset>

        <label className="control-field">
          <span>Horizon</span>
          <input
            type="number"
            min={1}
            step={1}
            value={settings.horizon}
            onChange={(event) => onChange(updateNumber(settings, "horizon", event.target.value))}
          />
        </label>

        <label className="control-field">
          <span>Seed</span>
          <input
            type="number"
            step={1}
            value={settings.seed}
            onChange={(event) => onChange(updateNumber(settings, "seed", event.target.value))}
          />
        </label>

        <label className="control-field">
          <span>Sliding window size</span>
          <input
            type="number"
            min={1}
            step={1}
            value={settings.windowSize}
            onChange={(event) =>
              onChange(updateNumber(settings, "windowSize", event.target.value))
            }
          />
        </label>

        <label className="control-field control-field-slider">
          <span>Epsilon</span>
          <div className="slider-row">
            <input
              type="range"
              min={0.01}
              max={0.5}
              step={0.01}
              value={settings.epsilon}
              onChange={(event) =>
                onChange({ ...settings, epsilon: Number(event.target.value) })
              }
              aria-describedby="lab-epsilon-value"
            />
            <output id="lab-epsilon-value" className="slider-value">
              {settings.epsilon.toFixed(2)}
            </output>
          </div>
        </label>
      </div>

      <fieldset className="control-group">
        <legend>Algorithms</legend>
        <div className="algorithm-grid">
          {ALGORITHM_OPTIONS.map((algorithm) => {
            const checked = settings.algorithms.includes(algorithm.value);

            return (
              <label
                key={algorithm.value}
                className={checked ? "algorithm-option is-checked" : "algorithm-option"}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={(event) => {
                    const algorithms = event.target.checked
                      ? [...settings.algorithms, algorithm.value]
                      : settings.algorithms.filter((value) => value !== algorithm.value);

                    onChange({ ...settings, algorithms });
                  }}
                />
                <span className="algorithm-copy">
                  <strong>{algorithm.label}</strong>
                  <span>{algorithm.detail}</span>
                </span>
              </label>
            );
          })}
        </div>
      </fieldset>

      <div className="lab-controls-footer">
        <p className="panel-note">
          Runs use the shared API client and fall back to fixtures if the backend is unavailable.
        </p>
        <button
          type="button"
          className="primary-action"
          onClick={onRun}
          disabled={isRunDisabled}
        >
          {isRunning ? "Running..." : "Run experiment"}
        </button>
      </div>
    </section>
  );
}
