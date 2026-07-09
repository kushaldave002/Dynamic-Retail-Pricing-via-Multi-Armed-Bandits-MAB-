import { FlaskConical, LayoutDashboard } from "lucide-react";
import type { ReactNode } from "react";

type TabKey = "overview" | "lab";

type TabItem = {
  key: TabKey;
  label: string;
  icon: ReactNode;
};

const TAB_ITEMS: TabItem[] = [
  {
    key: "overview",
    label: "Overview",
    icon: <LayoutDashboard size={16} aria-hidden="true" />,
  },
  {
    key: "lab",
    label: "Lab",
    icon: <FlaskConical size={16} aria-hidden="true" />,
  },
];

type TabsProps = {
  activeTab: TabKey;
  onChange: (tab: TabKey) => void;
};

export function Tabs({ activeTab, onChange }: TabsProps) {
  return (
    <div className="tab-list" role="tablist" aria-label="Pricing dashboard sections">
      {TAB_ITEMS.map((tab) => (
        <button
          key={tab.key}
          type="button"
          role="tab"
          aria-selected={activeTab === tab.key}
          className={activeTab === tab.key ? "tab is-active" : "tab"}
          onClick={() => onChange(tab.key)}
        >
          <span className="tab-icon">{tab.icon}</span>
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  );
}
