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
import { ALGORITHM_COLORS, formatAlgorithmName } from "../lab";
import type { TraceRow } from "../types";

const ROLLING_WINDOW = 10;

export function RewardTrendChart({ traces }: { traces: TraceRow[] }) {
  const grouped = traces.reduce<Record<string, TraceRow[]>>((acc, row) => {
    const existing = acc[row.algorithm] ?? [];
    existing.push(row);
    acc[row.algorithm] = existing;
    return acc;
  }, {});

  const stepMap = new Map<number, Record<string, number | string>>();

  Object.entries(grouped).forEach(([algorithm, rows]) => {
    const ordered = [...rows].sort((left, right) => left.step - right.step);

    ordered.forEach((row, index) => {
      const start = Math.max(0, index - ROLLING_WINDOW + 1);
      const windowRows = ordered.slice(start, index + 1);
      const average =
        windowRows.reduce((total, current) => total + current.reward, 0) / windowRows.length;
      const entry = stepMap.get(row.step) ?? { step: row.step };
      entry[algorithm] = Number(average.toFixed(2));
      stepMap.set(row.step, entry);
    });
  });

  const data = [...stepMap.values()].sort((left, right) => Number(left.step) - Number(right.step));
  const algorithms = Object.keys(grouped);

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
            formatter={(value: number) => [value.toFixed(2), "Rolling reward"]}
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
