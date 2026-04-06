import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export default function RiskChart({ predictions }) {

  if (!predictions || predictions.length === 0) {
    return <div className="card">No data available</div>;
  }

  const COLORS = ["#22c55e", "#facc15", "#ef4444"]; // Low, Medium, High

  return (
    <div className="card" style={{ height: "320px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>

          <Pie
            data={predictions}
            dataKey="value"
            nameKey="name"
            outerRadius={90}
            label
          >
            {predictions.map((entry, index) => (
              <Cell key={index} fill={COLORS[index]} />
            ))}
          </Pie>

          <Tooltip />
          <Legend />

        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}