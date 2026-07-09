import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TraceRow } from "../types";

const ARM_COLORS = ["#0f766e", "#0891b2", "#15803d", "#d97706", "#7c3aed"];

function formatAlgorithmName(algorithm: string) {
  return algorithm
    .split("_")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}

export function ArmShareChart({ traces }: { traces: TraceRow[] }) {
  const algorithmNames = Array.from(new Set(traces.map((trace) => trace.algorithm)));
  const armNames = Array.from(new Set(traces.map((trace) => trace.arm))).sort(
    (left, right) => left - right,
  );

  const grouped = traces.reduce<Record<string, Record<string, number | string>>>((acc, row) => {
    const existing = acc[row.algorithm] ?? { algorithm: formatAlgorithmName(row.algorithm), total: 0 };
    const armKey = `$${row.arm.toFixed(0)}`;
    existing[armKey] = Number(existing[armKey] ?? 0) + 1;
    existing.total = Number(existing.total) + 1;
    acc[row.algorithm] = existing;
    return acc;
  }, {});

  const data = algorithmNames.map((algorithm) => {
    const entry = grouped[algorithm] ?? { algorithm: formatAlgorithmName(algorithm), total: 0 };
    const total = Number(entry.total ?? 0);

    return armNames.reduce<Record<string, number | string>>(
      (acc, arm) => {
        const armKey = `$${arm.toFixed(0)}`;
        const pulls = Number(entry[armKey] ?? 0);
        acc[armKey] = total === 0 ? 0 : Number(((pulls / total) * 100).toFixed(1));
        return acc;
      },
      { algorithm: formatAlgorithmName(algorithm) },
    );
  });

  return (
    <div className="chart-shell">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="#d4dde8" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="algorithm"
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#5f6b7a", fontSize: 12 }}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#5f6b7a", fontSize: 12 }}
            unit="%"
            domain={[0, 100]}
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(1)}%`, "Arm share"]}
            contentStyle={{
              borderRadius: 8,
              border: "1px solid #d4dde8",
              background: "#ffffff",
              color: "#13202f",
            }}
          />
          <Legend />
          {armNames.map((arm, index) => {
            const armKey = `$${arm.toFixed(0)}`;

            return (
              <Bar
                key={armKey}
                dataKey={armKey}
                name={armKey}
                stackId="armShare"
                fill={ARM_COLORS[index % ARM_COLORS.length]}
              />
            );
          })}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
