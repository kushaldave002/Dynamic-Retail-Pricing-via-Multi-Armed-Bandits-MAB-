import type { SummaryRow } from "../types";

type StrategyTableProps = {
  summary: SummaryRow[];
};

function formatAlgorithmName(algorithm: string) {
  return algorithm
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

export function StrategyTable({ summary }: StrategyTableProps) {
  const sorted = [...summary].sort((left, right) => right.cumulative_reward - left.cumulative_reward);

  return (
    <div className="strategy-table-wrap">
      <table className="strategy-table">
        <thead>
          <tr>
            <th>Strategy</th>
            <th>Revenue</th>
            <th>Regret</th>
            <th>Best arm</th>
            <th>Pulls</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, index) => (
            <tr key={row.algorithm} className={index === 0 ? "is-leading" : undefined}>
              <td>
                <div className="strategy-name">
                  <span>{formatAlgorithmName(row.algorithm)}</span>
                  {index === 0 ? <span className="table-badge">Top</span> : null}
                </div>
              </td>
              <td>{row.cumulative_reward.toFixed(0)}</td>
              <td>{row.cumulative_regret.toFixed(0)}</td>
              <td>{row.best_arm.toFixed(2)}</td>
              <td>{row.pulls}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
