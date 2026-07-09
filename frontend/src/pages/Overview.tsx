import {
  AlertCircle,
  ArrowUpRight,
  BadgeDollarSign,
  Database,
  LineChart,
  Sparkles,
  Target,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { fetchPrecomputed } from "../api/client";
import { precomputedFixture } from "../api/fixtures";
import { RevenueRegretChart } from "../charts/RevenueRegretChart";
import { KpiCard } from "../components/KpiCard";
import { StrategyTable } from "../components/StrategyTable";
import type { DatasetCatalog, PrecomputedResponse, SummaryRow } from "../types";

type OverviewProps = {
  catalog: DatasetCatalog;
};

type ChartMetric = "cumulative_reward" | "cumulative_regret";

function formatAlgorithmName(algorithm: string) {
  return algorithm
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

function findBaseline(summary: SummaryRow[]) {
  return summary.find((row) => row.algorithm === "epsilon_greedy") ?? summary[0];
}

export function Overview({ catalog }: OverviewProps) {
  const [precomputed, setPrecomputed] = useState<PrecomputedResponse>(precomputedFixture);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [metric, setMetric] = useState<ChartMetric>("cumulative_reward");

  useEffect(() => {
    let cancelled = false;

    async function loadOverview() {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const payload = await fetchPrecomputed();
        if (!cancelled) {
          setPrecomputed(payload);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(error instanceof Error ? error.message : "Unable to load overview data.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadOverview();

    return () => {
      cancelled = true;
    };
  }, []);

  const sampleProduct = precomputed.sample_product;
  const summaries = precomputed.overview.summaries;

  const {
    winner,
    baseline,
    revenueLift,
    revenueLiftPct,
    regretReduction,
    regretReductionPct,
  } = useMemo(() => {
    const ordered = [...summaries].sort(
      (left, right) => right.cumulative_reward - left.cumulative_reward,
    );
    const lead = ordered[0];
    const baselineRow = findBaseline(ordered);
    const rewardDelta = lead.cumulative_reward - baselineRow.cumulative_reward;
    const regretDelta = baselineRow.cumulative_regret - lead.cumulative_regret;

    return {
      winner: lead,
      baseline: baselineRow,
      revenueLift: rewardDelta,
      revenueLiftPct:
        baselineRow.cumulative_reward === 0
          ? 0
          : (rewardDelta / baselineRow.cumulative_reward) * 100,
      regretReduction: regretDelta,
      regretReductionPct:
        baselineRow.cumulative_regret === 0
          ? 0
          : (regretDelta / baselineRow.cumulative_regret) * 100,
    };
  }, [summaries]);

  const datasetCount = catalog.products.length || 1;
  const priceArmRange = `${Math.min(...sampleProduct.price_arms).toFixed(0)} to ${Math.max(
    ...sampleProduct.price_arms,
  ).toFixed(0)}`;

  if (errorMessage) {
    return (
      <section className="overview-empty-state" aria-live="polite">
        <AlertCircle size={18} aria-hidden="true" />
        <div>
          <h2>Overview unavailable</h2>
          <p>{errorMessage}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="overview-page">
      <div className="overview-band">
        <div className="overview-heading">
          <div>
            <p className="section-kicker">Executive summary</p>
            <h2>Precomputed policy comparison for {sampleProduct.name}</h2>
            <p className="section-intro">
              Readout for recruiter screening and ML review: how fast each policy finds the
              strongest retail price arm, what it leaves on the table, and which strategy wins on
              observed reward.
            </p>
          </div>
          <div className="price-ladder" aria-label="Observed price ladder">
            {sampleProduct.price_arms.map((arm) => {
              const isWinnerArm = arm === winner.best_arm;
              return (
                <div
                  key={arm}
                  className={isWinnerArm ? "ladder-rung is-winner" : "ladder-rung"}
                >
                  <span>${arm.toFixed(0)}</span>
                  <span>{isWinnerArm ? "Lead arm" : "Candidate"}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="kpi-strip">
          <KpiCard
            label="Winning policy"
            value={formatAlgorithmName(winner.algorithm)}
            detail={`${winner.cumulative_reward.toFixed(0)} cumulative revenue`}
            tone="neutral"
          />
          <KpiCard
            label="Revenue lift vs Epsilon-Greedy"
            value={`+${revenueLift.toFixed(0)}`}
            detail={`${revenueLiftPct.toFixed(1)}% higher return`}
            tone="revenue"
          />
          <KpiCard
            label="Regret reduction"
            value={`${regretReduction.toFixed(0)}`}
            detail={`${regretReductionPct.toFixed(1)}% lower regret`}
            tone="regret"
          />
          <KpiCard
            label="Observed price arms"
            value={String(sampleProduct.price_arms.length)}
            detail={`Range ${priceArmRange}`}
            tone="exploration"
          />
        </div>
      </div>

      <div className="overview-main-grid">
        <section className="dashboard-panel chart-panel">
          <div className="panel-topline">
            <div>
              <p className="panel-kicker">Trace behavior</p>
              <h3>Revenue and regret over decision steps</h3>
            </div>
            <div className="segmented-control" role="tablist" aria-label="Chart metric">
              <button
                type="button"
                className={metric === "cumulative_reward" ? "segment is-active" : "segment"}
                onClick={() => setMetric("cumulative_reward")}
              >
                Revenue
              </button>
              <button
                type="button"
                className={metric === "cumulative_regret" ? "segment is-active" : "segment"}
                onClick={() => setMetric("cumulative_regret")}
              >
                Regret
              </button>
            </div>
          </div>
          <RevenueRegretChart traces={precomputed.overview.traces} metric={metric} />
          <p className="panel-note">
            {metric === "cumulative_reward"
              ? "Higher is better. Teal and green traces should separate quickly if a policy exploits strong arms efficiently."
              : "Lower is better. Early exploration creates some regret; the stronger policy flattens faster."}
          </p>
        </section>

        <section className="dashboard-panel narrative-panel">
          <div className="panel-topline">
            <div>
              <p className="panel-kicker">Interpretation</p>
              <h3>What the review panel should notice</h3>
            </div>
            <span className={isLoading ? "status-badge is-loading" : "status-badge"}>
              {isLoading ? "Loading" : precomputed.source}
            </span>
          </div>
          <div className="narrative-list">
            <div className="narrative-item">
              <BadgeDollarSign size={18} aria-hidden="true" />
              <p>
                <strong>{formatAlgorithmName(winner.algorithm)}</strong> leads this run, producing{" "}
                {revenueLift.toFixed(0)} more cumulative revenue than{" "}
                {formatAlgorithmName(baseline.algorithm)} while converging on the{" "}
                ${winner.best_arm.toFixed(2)} price arm.
              </p>
            </div>
            <div className="narrative-item">
              <Target size={18} aria-hidden="true" />
              <p>
                Regret falls by {regretReduction.toFixed(0)} against the epsilon baseline, which
                reads as fewer low-yield pricing decisions during the learning window.
              </p>
            </div>
            <div className="narrative-item">
              <Sparkles size={18} aria-hidden="true" />
              <p>
                Counterfactual demand is simulated from historical retail transactions, so the
                dashboard demonstrates policy behavior rather than causal proof.
              </p>
            </div>
          </div>
        </section>

        <section className="dashboard-panel">
          <div className="panel-topline">
            <div>
              <p className="panel-kicker">Strategy ranking</p>
              <h3>Summary table</h3>
            </div>
            <LineChart size={18} aria-hidden="true" />
          </div>
          <StrategyTable summary={summaries} />
        </section>

        <section className="dashboard-panel dataset-panel">
          <div className="panel-topline">
            <div>
              <p className="panel-kicker">Dataset context</p>
              <h3>Sample and defaults</h3>
            </div>
            <Database size={18} aria-hidden="true" />
          </div>
          <dl className="dataset-grid">
            <div>
              <dt>Sample product</dt>
              <dd>{sampleProduct.name}</dd>
            </div>
            <div>
              <dt>Observations</dt>
              <dd>{sampleProduct.observations}</dd>
            </div>
            <div>
              <dt>Dataset source</dt>
              <dd>{catalog.source}</dd>
            </div>
            <div>
              <dt>Records in catalog</dt>
              <dd>{datasetCount}</dd>
            </div>
            <div>
              <dt>Environment</dt>
              <dd>{precomputed.lab_defaults.environment}</dd>
            </div>
            <div>
              <dt>Seed / horizon</dt>
              <dd>
                {precomputed.lab_defaults.seed} / {precomputed.lab_defaults.horizon}
              </dd>
            </div>
          </dl>
          <div className="dataset-footer">
            <span>Arms {sampleProduct.price_arms.map((arm) => `$${arm.toFixed(0)}`).join(", ")}</span>
            <span className="dataset-link">
              <ArrowUpRight size={14} aria-hidden="true" />
              {precomputed.lab_defaults.sample_source}
            </span>
          </div>
        </section>
      </div>
    </section>
  );
}
