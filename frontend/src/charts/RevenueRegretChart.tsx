import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TraceRow } from "../types";

type Props = {
  traces: TraceRow[];
  metric: "cumulative_reward" | "cumulative_regret";
};

const ALGORITHM_COLORS: Record<string, string> = {
  epsilon_greedy: "#d97706",
  ucb1: "#0891b2",
  sliding_window_ucb: "#0f766e",
  thompson_sampling: "#15803d",
};

function formatAlgorithmName(algorithm: string) {
  return algorithm
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

export function RevenueRegretChart({ traces, metric }: Props) {
  const grouped = traces.reduce<Record<number, Record<string, number | string>>>((acc, row) => {
    const existing = acc[row.step] ?? { step: row.step };
    existing[row.algorithm] = row[metric];
    acc[row.step] = existing;
    return acc;
  }, {});

  const data = Object.values(grouped).sort(
    (left, right) => Number(left.step) - Number(right.step),
  );

  const algorithms = Array.from(new Set(traces.map((trace) => trace.algorithm)));

  return (
    <div className="chart-shell">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="#d4dde8" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="step"
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#5f6b7a", fontSize: 12 }}
          />
          <YAxis tickLine={false} axisLine={false} tick={{ fill: "#5f6b7a", fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              borderRadius: 8,
              border: "1px solid #d4dde8",
              background: "#ffffff",
              color: "#13202f",
            }}
          />
          <Legend />
          {algorithms.map((algorithm) => (
            <Line
              key={algorithm}
              type="monotone"
              dataKey={algorithm}
              name={formatAlgorithmName(algorithm)}
              stroke={ALGORITHM_COLORS[algorithm] ?? "#334155"}
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
