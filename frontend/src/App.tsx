import { Database, RadioTower } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchDatasets } from "./api/client";
import { Tabs } from "./components/Tabs";
import { Lab } from "./pages/Lab";
import { Overview } from "./pages/Overview";
import type { DatasetCatalog } from "./types";

type TabKey = "overview" | "lab";

const INITIAL_CATALOG: DatasetCatalog = {
  source: "loading",
  products: [],
};

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [catalog, setCatalog] = useState<DatasetCatalog>(INITIAL_CATALOG);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const catalogPayload = await fetchDatasets();

      if (cancelled) {
        return;
      }

      setCatalog(catalogPayload);
      setIsLoading(false);
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-title-block">
          <p className="eyebrow">Executive pricing analytics</p>
          <h1>Dynamic Retail Pricing Dashboard</h1>
          <p className="hero-text">
            Quiet readout of precomputed bandit behavior for retail pricing experiments, aimed at
            recruiter walkthroughs and technical reviewers.
          </p>
        </div>
        <div className="header-meta">
          <div className="meta-chip">
            <Database size={16} aria-hidden="true" />
            <span>{isLoading ? "Loading catalog" : `${catalog.products.length} catalog product${catalog.products.length === 1 ? "" : "s"}`}</span>
          </div>
          <div className="meta-chip">
            <RadioTower size={16} aria-hidden="true" />
            <span>API base {import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"}</span>
          </div>
        </div>
      </header>

      <main className="content-shell">
        <Tabs activeTab={activeTab} onChange={setActiveTab} />
        {activeTab === "overview" ? (
          <Overview catalog={catalog} />
        ) : (
          <Lab catalog={catalog} />
        )}
      </main>
    </div>
  );
}

