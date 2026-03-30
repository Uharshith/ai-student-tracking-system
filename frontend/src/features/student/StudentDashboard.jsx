import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import studentService from "../../api/studentService";
import "../../styles/dashboard.css";

export default function StudentDashboard() {
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await studentService.getRecommendation();
      setData(res.data);
    } catch (err) {
      console.error("Dashboard error:", err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="student-dashboard">Loading...</div>;
  if (!data) return <div className="student-dashboard">No data found</div>;

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
          <div className="kpi-title">Attendance</div>
          <div className="kpi-value">
            {data.attendance_percentage}%
          </div>
        </div>

        <div
          className="kpi-card clickable"
          onClick={() => navigate("/student/marks")}
        >
          <div className="kpi-title">Average Marks</div>
          <div className="kpi-value">
            {data.average_marks}%
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Performance Level</div>
          <div
            className={`kpi-value ${
              data.performance_level === "High"
                ? "success"
                : data.performance_level === "Medium"
                ? "warning"
                : "danger"
            }`}
          >
            {data.performance_level}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Risk Level</div>
          <div
            className={`kpi-value ${
              data.risk_level === "Low"
                ? "success"
                : data.risk_level === "Medium"
                ? "warning"
                : "danger"
            }`}
          >
            {data.risk_level}
          </div>
        </div>

      </div>

      {/* Recommendation Section */}
      <div className="chart-container">
        <h3>AI Recommendations</h3>
        <div className="chart-box">
          {data.recommendations?.length > 0 ? (
            <ul>
              {data.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          ) : (
            <p>No recommendations available</p>
          )}
        </div>
      </div>

    </div>
  );
}