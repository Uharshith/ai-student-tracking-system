import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import studentService from "../../api/studentService";
import RiskChart from "../../components/charts/RiskChart";
import "../../styles/dashboard.css";

export default function StudentDashboard() {
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [ai, setAI] = useState(null);
  const [riskData, setRiskData] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      // 🔥 CALL BOTH APIs
      const statsRes = await studentService.getCurrentSemStats();
      const pieRes = await studentService.getRiskPieChart();

      setStats(statsRes.data);
      setAI(statsRes.data);

      // 🔥 IMPORTANT FIX (USE pie_data)
      setRiskData(pieRes.data.pie_data);

    } catch (err) {
      console.error("Dashboard error:", err.response?.data || err.message);
      setError("Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="student-dashboard">Loading...</div>;
  if (error) return <div className="student-dashboard">{error}</div>;

  return (
    <div className="student-dashboard">

      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1>Welcome Back 👋</h1>
          <p>Your academic performance overview</p>
        </div>
        <div className="badge">Student</div>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">

        <div
          className="kpi-card clickable"
          onClick={() => navigate("/student/attendance")}
        >
          <div className="kpi-title">Current Sem Attendance</div>
          <div className="kpi-value">
            {stats?.attendance ?? 0}%
          </div>
        </div>

        <div
          className="kpi-card clickable"
          onClick={() => navigate("/student/marks")}
        >
          <div className="kpi-title">Current Sem Avg Marks</div>
          <div className="kpi-value">
            {stats?.average_marks > 0 ? stats.average_marks : "N/A"}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Performance Level</div>
          <div
            className={`kpi-value ${
              ai?.performance_level === "High"
                ? "success"
                : ai?.performance_level === "Medium"
                ? "warning"
                : "danger"
            }`}
          >
            {ai?.performance_level || "N/A"}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Risk Level</div>
          <div
            className={`kpi-value ${
              ai?.risk_level === "Low"
                ? "success"
                : ai?.risk_level === "Medium"
                ? "warning"
                : "danger"
            }`}
          >
            {ai?.risk_level || "N/A"}
          </div>
        </div>

      </div>

      {/* AI Recommendations */}
      <div className="chart-container">
        <h3>AI Recommendations</h3>
        <div className="chart-box">
          {ai?.recommendations?.length > 0 ? (
            <ul>
              {ai.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          ) : (
            <p>No recommendations available</p>
          )}
        </div>
      </div>

      {/* 🔥 FIXED Risk Chart */}
      <div className="chart-container">
        <h3>Risk Distribution</h3>
        <RiskChart predictions={riskData} />
      </div>

    </div>
  );
}