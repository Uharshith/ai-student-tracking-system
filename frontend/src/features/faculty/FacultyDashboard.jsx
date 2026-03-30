import { useEffect, useState } from "react";
import {
  getFacultyDashboard,
  getPerformanceTrend,
  getSubjectBreakdown,
} from "../../api/facultyService";
import "../../styles/dashboard.css";
import Loader from "../../components/common/Loader";

import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function FacultyDashboard() {
  const [data, setData] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [subjectData, setSubjectData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        // Fetch all in parallel (better performance)
        const [dashboard, trend, breakdown] = await Promise.all([
          getFacultyDashboard(),
          getPerformanceTrend(),
          getSubjectBreakdown(),
        ]);

        setData(dashboard);

        // Format month nicely
        const formattedTrend = trend.map((item) => ({
          ...item,
          month: item.month
            ? new Date(item.month).toLocaleString("default", {
                month: "short",
              })
            : "",
        }));

        setTrendData(formattedTrend);
        setSubjectData(breakdown);
      } catch (error) {
        console.error("Dashboard error:", error.response?.data || error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading || !data) return <Loader />;

  return (
    <div className="faculty-dashboard">

      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1>Faculty Dashboard 👨‍🏫</h1>
          <p>Monitor class performance and manage academic records</p>
        </div>
        <div className="badge faculty-badge">Faculty</div>
      </div>

      {/* KPI Section */}
      <div className="kpi-grid">

        <div className="kpi-card">
          <div className="kpi-title">Total Students</div>
          <div className="kpi-value">{data.total_students}</div>
          <div className="kpi-change neutral">Across department</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Class Attendance</div>
          <div className="kpi-value">{data.attendance_percentage}%</div>
          <div className="kpi-change neutral">Overall attendance</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Average Marks</div>
          <div className="kpi-value">{data.average_marks}%</div>
          <div className="kpi-change neutral">Across subjects</div>
        </div>

        <div className="kpi-card danger-card">
          <div className="kpi-title">Students At Risk</div>
          <div className="kpi-value danger">{data.at_risk_students}</div>
          <div className="kpi-change danger">Marks below 40</div>
        </div>

      </div>

      {/* Performance Trend Line Chart */}
      <div className="chart-container">
        <h3>Performance Trend</h3>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="avg_marks"
                stroke="#4c5fd7"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Subject-wise Breakdown Bar Chart */}
      <div className="chart-container">
        <h3>Subject-wise Performance</h3>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={subjectData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="subject" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="avg_marks" fill="#5e72e4" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}