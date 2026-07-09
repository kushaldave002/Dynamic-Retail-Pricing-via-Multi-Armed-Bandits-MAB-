import { AlertCircle, FlaskConical, Loader2, Sparkles, Trophy } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { runExperiment } from "../api/client";
import { ArmShareChart } from "../charts/ArmShareChart";
import { RevenueRegretChart } from "../charts/RevenueRegretChart";
import { RewardTrendChart } from "../charts/RewardTrendChart";
import { KpiCard } from "../components/KpiCard";
import { LabControls, type LabSettings } from "../components/LabControls";
import type { DatasetCatalog, ExperimentRequest, ExperimentResponse, SummaryRow } from "../types";

type LabProps = {
  catalog: DatasetCatalog;
};

const DEFAULT_SETTINGS: LabSettings = {
  environment: "elasticity",
  horizon: 200,
  seed: 42,
  algorithms: ["epsilon_greedy", "ucb1", "sliding_window_ucb", "thompson_sampling"],
  epsilon: 0.1,
  windowSize: 50,
};

function formatAlgorithmName(algorithm: string) {
  return algorithm
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function findBaseline(summary: SummaryRow[]) {
  return summary.find((row) => row.algorithm === "epsilon_greedy") ?? summary[0];
}

function buildRequest(settings: LabSettings): ExperimentRequest {
  return {
    environment: settings.environment,
    horizon: settings.horizon,
    seed: settings.seed,
    algorithms: settings.algorithms,
    parameters: {
      epsilon_greedy: { epsilon: settings.epsilon },
      sliding_window_ucb: { window_size: settings.windowSize },
      ucb1: {},
      thompson_sampling: {},
    },
  };
}

export function Lab({ catalog }: LabProps) {
  const [settings, setSettings] = useState<LabSettings>(DEFAULT_SETTINGS);
  const [result, setResult] = useState<ExperimentResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const executeRun = useCallback(async (nextSettings: LabSettings) => {
    setIsRunning(true);
    setErrorMessage(null);

    try {
      const payload = await runExperiment(buildRequest(nextSettings));
      setResult(payload);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to run experiment.");
    } finally {
      setIsRunning(false);
    }
  }, []);

  useEffect(() => {
    void executeRun(DEFAULT_SETTINGS);
  }, [executeRun]);

  const orderedSummary = useMemo(() => {
    return result
      ? [...result.summary].sort((left, right) => right.cumulative_reward - left.cumulative_reward)
      : [];
  }, [result]);

  const winner = orderedSummary[0];
  const baseline = orderedSummary.length > 0 ? findBaseline(orderedSummary) : null;
  const revenueLift =
    winner && baseline ? winner.cumulative_reward - baseline.cumulative_reward : 0;
  const regretReduction =
    winner && baseline ? baseline.cumulative_regret - winner.cumulative_regret : 0;
  const revenueLiftPct =
    winner && baseline && baseline.cumulative_reward !== 0
      ? (revenueLift / baseline.cumulative_reward) * 100
      : 0;

  return (
    <section className="lab-page">
      <div className="lab-grid">
        <LabControls
          settings={settings}
          onChange={setSettings}
          onRun={() => void executeRun(settings)}
          isRunning={isRunning}
        />

        {errorMessage ? (
          <section className="overview-empty-state" aria-live="polite">
            <AlertCircle size={18} aria-hidden="true" />
            <div>
              <h2>Experiment unavailable</h2>
              <p>{errorMessage}</p>
            </div>
          </section>
        ) : null}

        {!errorMessage && isRunning && result === null ? (
          <section className="overview-loading-state" aria-live="polite" aria-busy="true">
            <Loader2 size={18} className="loading-spinner" aria-hidden="true" />
            <div>
              <h2>Running experiment</h2>
              <p>Submitting the default Lab configuration and waiting for the first response.</p>
            </div>
          </section>
        ) : null}

        {result ? (
          <>
            <div className="kpi-strip">
              <KpiCard
                label="Winner"
                value={winner ? formatAlgorithmName(winner.algorithm) : "Unavailable"}
                detail={
                  winner
                    ? `${winner.cumulative_reward.toFixed(0)} cumulative revenue`
                    : "No summary rows returned"
                }
                tone="neutral"
              />
              <KpiCard
                label="Revenue lift"
                value={baseline ? `+${revenueLift.toFixed(0)}` : "0"}
                detail={
                  baseline
                    ? `${revenueLiftPct.toFixed(1)}% vs ${formatAlgorithmName(baseline.algorithm)}`
                    : "Baseline unavailable"
                }
                tone="revenue"
              />
              <KpiCard
                label="Regret reduction"
                value={baseline ? regretReduction.toFixed(0) : "0"}
                detail={
                  baseline ? `Vs ${formatAlgorithmName(baseline.algorithm)}` : "Baseline unavailable"
                }
                tone="regret"
              />
              <KpiCard
                label="Selected algorithms"
                value={String(settings.algorithms.length)}
                detail={`${result.sample_product.price_arms.length} price arms`}
                tone="exploration"
              />
            </div>

            <div className="lab-panels-grid">
              <section className="dashboard-panel chart-panel">
                <div className="panel-topline">
                  <div>
                    <p className="panel-kicker">Cumulative revenue</p>
                    <h3>Observed reward over decision steps</h3>
                  </div>
                </div>
                <RevenueRegretChart traces={result.traces} metric="cumulative_reward" />
              </section>

              <section className="dashboard-panel chart-panel">
                <div className="panel-topline">
                  <div>
                    <p className="panel-kicker">Cumulative regret</p>
                    <h3>Opportunity cost through the run</h3>
                  </div>
                </div>
                <RevenueRegretChart traces={result.traces} metric="cumulative_regret" />
              </section>

              <section className="dashboard-panel chart-panel">
                <div className="panel-topline">
                  <div>
                    <p className="panel-kicker">Arm share</p>
                    <h3>Which price arms each policy favors</h3>
                  </div>
                </div>
                <ArmShareChart traces={result.traces} />
              </section>

              <section className="dashboard-panel chart-panel">
                <div className="panel-topline">
                  <div>
                    <p className="panel-kicker">Reward trend</p>
                    <h3>Rolling 10-step average reward</h3>
                  </div>
                </div>
                <RewardTrendChart traces={result.traces} />
              </section>

              <section className="dashboard-panel">
                <div className="panel-topline">
                  <div>
                    <p className="panel-kicker">Winner summary</p>
                    <h3>What changed in this run</h3>
                  </div>
                  <span className={isRunning ? "status-badge is-loading" : "status-badge"}>
                    {isRunning ? "Refreshing" : result.source}
                  </span>
                </div>
                <div className="narrative-list">
                  <div className="narrative-item">
                    <Trophy size={18} aria-hidden="true" />
                    <p>
                      <strong>{winner ? formatAlgorithmName(winner.algorithm) : "No winner"}</strong>
                      {winner
                        ? ` leads the ${settings.environment} run on ${result.sample_product.name}, finishing on the $${winner.best_arm.toFixed(2)} arm.`
                        : " No summary rows were returned for this run."}
                    </p>
                  </div>
                  <div className="narrative-item">
                    <FlaskConical size={18} aria-hidden="true" />
                    <p>
                      Horizon {settings.horizon}, seed {settings.seed}, epsilon{" "}
                      {settings.epsilon.toFixed(2)}, and sliding window {settings.windowSize} shape
                      this replay.
                    </p>
                  </div>
                  <div className="narrative-item">
                    <Sparkles size={18} aria-hidden="true" />
                    <p>
                      Catalog source {catalog.source} with {catalog.products.length} product
                      {catalog.products.length === 1 ? "" : "s"} available; this chart set reflects
                      the sample product returned by the run endpoint.
                    </p>
                  </div>
                </div>
              </section>
            </div>
          </>
        ) : null}
      </div>
    </section>
  );
}
