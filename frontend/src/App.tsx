import { Database, RadioTower, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { fetchDatasets, fetchPrecomputed } from "./api/client";
import { precomputedFixture } from "./api/fixtures";
import { Tabs } from "./components/Tabs";
import type { DatasetCatalog, PrecomputedResponse } from "./types";

type TabKey = "overview" | "lab";

const INITIAL_CATALOG: DatasetCatalog = {
  source: "loading",
  products: [],
};

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [catalog, setCatalog] = useState<DatasetCatalog>(INITIAL_CATALOG);
  const [precomputed, setPrecomputed] = useState<PrecomputedResponse>(precomputedFixture);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const [catalogPayload, precomputedPayload] = await Promise.all([
        fetchDatasets(),
        fetchPrecomputed(),
      ]);

      if (cancelled) {
        return;
      }

      setCatalog(catalogPayload);
      setPrecomputed(precomputedPayload);
      setIsLoading(false);
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const sampleProduct = precomputed.sample_product;
  const metricSummary = useMemo(() => {
    return precomputed.overview.summaries.map((row) => ({
      ...row,
      revenueLabel: row.cumulative_reward.toFixed(0),
      regretLabel: row.cumulative_regret.toFixed(0),
    }));
  }, [precomputed]);

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Retail pricing simulation scaffold</p>
          <h1>Dynamic Retail Pricing Lab</h1>
          <p className="hero-text">
            Base shell for the React dashboard, wired to FastAPI when available and falling back
            to compact local fixtures during frontend-only work.
          </p>
        </div>
        <div className="hero-meta">
          <div className="meta-chip">
            <Database size={16} aria-hidden="true" />
            <span>{catalog.products.length || 1} sample product</span>
          </div>
          <div className="meta-chip">
            <RadioTower size={16} aria-hidden="true" />
            <span>API base {import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"}</span>
          </div>
        </div>
      </header>

      <main className="content">
        <Tabs activeTab={activeTab} onChange={setActiveTab} />

        <section className="panel-grid">
          <article className="panel panel-primary">
            <div className="panel-heading">
              <h2>{activeTab === "overview" ? "Overview scaffold" : "Lab scaffold"}</h2>
              <span className="status-pill">{isLoading ? "Loading" : "Ready"}</span>
            </div>

            {activeTab === "overview" ? (
              <div className="stack">
                <p className="section-copy">
                  Task 7 stops at the app shell. The next task will replace this placeholder with
                  KPI cards, charts, and comparison tables.
                </p>
                <div className="stat-row">
                  {metricSummary.map((row) => (
                    <div key={row.algorithm} className="stat-block">
                      <span className="stat-label">{row.algorithm}</span>
                      <strong>{row.revenueLabel}</strong>
                      <span>regret {row.regretLabel}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="stack">
                <p className="section-copy">
                  Task 9 will add the interactive controls and result charts. The scaffold already
                  exposes typed request and response helpers for that work.
                </p>
                <div className="lab-defaults">
                  <div>
                    <span className="detail-label">Environment</span>
                    <strong>{precomputed.lab_defaults.environment}</strong>
                  </div>
                  <div>
                    <span className="detail-label">Horizon</span>
                    <strong>{precomputed.lab_defaults.horizon}</strong>
                  </div>
                  <div>
                    <span className="detail-label">Algorithms</span>
                    <strong>{precomputed.lab_defaults.algorithms.join(", ")}</strong>
                  </div>
                </div>
              </div>
            )}
          </article>

          <article className="panel">
            <div className="panel-heading">
              <h2>Fixture and API data</h2>
              <span className="source-badge">{precomputed.source}</span>
            </div>
            <div className="stack">
              <div className="detail-grid">
                <div>
                  <span className="detail-label">Sample product</span>
                  <strong>{sampleProduct.name}</strong>
                </div>
                <div>
                  <span className="detail-label">Dataset source</span>
                  <strong>{catalog.source}</strong>
                </div>
                <div>
                  <span className="detail-label">Observation count</span>
                  <strong>{sampleProduct.observations}</strong>
                </div>
                <div>
                  <span className="detail-label">Price arms</span>
                  <strong>{sampleProduct.price_arms.join(", ")}</strong>
                </div>
              </div>
              <div className="trace-preview">
                <div className="trace-header">
                  <SlidersHorizontal size={16} aria-hidden="true" />
                  <span>Trace preview</span>
                </div>
                <ul>
                  {precomputed.overview.traces.slice(0, 4).map((trace) => (
                    <li key={`${trace.algorithm}-${trace.step}`}>
                      <span>{trace.algorithm}</span>
                      <span>step {trace.step}</span>
                      <span>arm {trace.arm}</span>
                      <span>reward {trace.reward}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}
