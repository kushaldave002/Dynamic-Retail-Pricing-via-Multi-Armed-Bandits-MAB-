import { AlertCircle, FlaskConical, Loader2, Sparkles, Trophy } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { runExperiment } from "../api/client";
import { ArmShareChart } from "../charts/ArmShareChart";
import { RevenueRegretChart } from "../charts/RevenueRegretChart";
import { RewardTrendChart } from "../charts/RewardTrendChart";
import { KpiCard } from "../components/KpiCard";
import { LabControls } from "../components/LabControls";
import {
  areLabSettingsEqual,
  buildExperimentRequest,
  DEFAULT_LAB_SETTINGS,
  formatAlgorithmName,
  type LabSettings,
  normalizeLabSettings,
} from "../lab";
import type { DatasetCatalog, ExperimentResponse, SummaryRow } from "../types";

type LabProps = {
  catalog: DatasetCatalog;
};

function findBaseline(summary: SummaryRow[]) {
  return summary.find((row) => row.algorithm === "epsilon_greedy") ?? summary[0];
}

export function Lab({ catalog }: LabProps) {
  const [settings, setSettings] = useState<LabSettings>(DEFAULT_LAB_SETTINGS);
  const [result, setResult] = useState<ExperimentResponse | null>(null);
  const [lastRunSettings, setLastRunSettings] = useState<LabSettings | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const executeRun = useCallback(async (nextSettings: LabSettings) => {
    const normalizedSettings = normalizeLabSettings(nextSettings);

    setIsRunning(true);
    setErrorMessage(null);

    try {
      const payload = await runExperiment(buildExperimentRequest(normalizedSettings));
      setResult(payload);
      setLastRunSettings(normalizedSettings);
      setSettings(normalizedSettings);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to run experiment.");
    } finally {
      setIsRunning(false);
    }
  }, []);

  const orderedSummary = useMemo(() => {
    return result
      ? [...result.summary].sort((left, right) => right.cumulative_reward - left.cumulative_reward)
      : [];
  }, [result]);
  const normalizedSettings = useMemo(() => normalizeLabSettings(settings), [settings]);
  const displayedSettings = lastRunSettings ?? DEFAULT_LAB_SETTINGS;
  const hasSettingsChanged =
    result !== null &&
    lastRunSettings !== null &&
    !areLabSettingsEqual(normalizedSettings, lastRunSettings);

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
          settings={normalizedSettings}
          onChange={(nextSettings) => setSettings(normalizeLabSettings(nextSettings))}
          onRun={() => void executeRun(normalizedSettings)}
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
              <p>Submitting the current Lab configuration and waiting for the response.</p>
            </div>
          </section>
        ) : null}

        {!errorMessage && !isRunning && result === null ? (
          <section className="overview-loading-state" aria-live="polite">
            <FlaskConical size={18} aria-hidden="true" />
            <div>
              <h2>Ready to run</h2>
              <p>
                Start with the default {DEFAULT_LAB_SETTINGS.environment} setup: horizon{" "}
                {DEFAULT_LAB_SETTINGS.horizon}, seed {DEFAULT_LAB_SETTINGS.seed}, epsilon{" "}
                {DEFAULT_LAB_SETTINGS.epsilon.toFixed(2)}, and sliding window{" "}
                {DEFAULT_LAB_SETTINGS.windowSize}.
              </p>
            </div>
          </section>
        ) : null}

        {result ? (
          <>
            {hasSettingsChanged ? (
              <section className="settings-warning" aria-live="polite">
                <AlertCircle size={18} aria-hidden="true" />
                <p>
                  Settings changed since the last successful run. Run again to refresh the summary
                  and charts.
                </p>
              </section>
            ) : null}

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
                  baseline
                    ? `Vs ${formatAlgorithmName(baseline.algorithm)}`
                    : "Baseline unavailable"
                }
                tone="regret"
              />
              <KpiCard
                label="Selected algorithms"
                value={String(displayedSettings.algorithms.length)}
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
                  <span
                    className={
                      isRunning
                        ? "status-badge is-loading"
                        : hasSettingsChanged
                          ? "status-badge is-warning"
                          : "status-badge"
                    }
                  >
                    {isRunning ? "Refreshing" : hasSettingsChanged ? "Run again" : result.source}
                  </span>
                </div>
                <div className="narrative-list">
                  <div className="narrative-item">
                    <Trophy size={18} aria-hidden="true" />
                    <p>
                      <strong>{winner ? formatAlgorithmName(winner.algorithm) : "No winner"}</strong>
                      {winner
                        ? ` leads the ${displayedSettings.environment} run on ${result.sample_product.name}, finishing on the $${winner.best_arm.toFixed(2)} arm.`
                        : " No summary rows were returned for this run."}
                    </p>
                  </div>
                  <div className="narrative-item">
                    <FlaskConical size={18} aria-hidden="true" />
                    <p>
                      Horizon {displayedSettings.horizon}, seed {displayedSettings.seed}, epsilon{" "}
                      {displayedSettings.epsilon.toFixed(2)}, and sliding window{" "}
                      {displayedSettings.windowSize} shaped this replay.
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
