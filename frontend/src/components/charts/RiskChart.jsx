import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function RiskChart({ predictions }) {

  if (!predictions || predictions.length === 0) return null;

  let low = 0;
  let medium = 0;
  let high = 0;

  predictions.forEach((item) => {

    const risk = item.risk.toUpperCase();

    if (risk.includes("LOW")) low++;
    else if (risk.includes("MEDIUM")) medium++;
    else if (risk.includes("HIGH")) high++;

  });

  const data = [
    { name: "LOW", value: low },
    { name: "MEDIUM", value: medium },
    { name: "HIGH", value: high },
  ];

  const COLORS = ["#22c55e", "#facc15", "#ef4444"];

  return (
    <div className="card" style={{ height: "300px" }}>
      <h3>Subject Risk Distribution</h3>

      <ResponsiveContainer width="100%" height="100%">
        <PieChart>

          <Pie
            data={data}
            dataKey="value"
            outerRadius={80}
          >

            {data.map((entry, index) => (
              <Cell key={index} fill={COLORS[index]} />
            ))}

          </Pie>

          <Tooltip />

        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}