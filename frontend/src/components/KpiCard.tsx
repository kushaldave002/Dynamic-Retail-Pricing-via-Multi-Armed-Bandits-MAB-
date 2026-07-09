type KpiCardProps = {
  label: string;
  value: string;
  detail: string;
  tone?: "neutral" | "revenue" | "regret" | "exploration";
};

export function KpiCard({ label, value, detail, tone = "neutral" }: KpiCardProps) {
  return (
    <article className={`kpi-card tone-${tone}`}>
      <span className="kpi-label">{label}</span>
      <strong className="kpi-value">{value}</strong>
      <span className="kpi-detail">{detail}</span>
    </article>
  );
}
