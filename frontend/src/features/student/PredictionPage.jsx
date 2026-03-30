import { useEffect, useState } from "react";
import predictionService from "../../api/predictionService";
import Loader from "../../components/common/Loader";
import "../../styles/prediction.css";

export default function PredictionPage() {

  const userName = "Dinku";

  const [semester, setSemester] = useState(1);

  const [predictions, setPredictions] = useState([]);
  const [trendAnalysis, setTrendAnalysis] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ✅ ONLY TREND CONTROL
  const [showTrend, setShowTrend] = useState(false);

  useEffect(() => {
    fetchPrediction();
  }, [semester]);

  const fetchPrediction = async () => {
    try {
      setLoading(true);

      const subjectRisk = await predictionService.getSubjectRisk(semester);
      const recommendation = await predictionService.getRecommendation(semester);

      setPredictions(subjectRisk || []);
      setTrendAnalysis(recommendation?.trend_analysis || []);
      setRecommendations(recommendation?.recommendations || []);

    } catch (err) {
      console.error("Prediction Error:", err);
      setError("Unable to load prediction data");
    } finally {
      setLoading(false);
    }
  };

  const getRiskClass = (risk) => {
    if (!risk) return "";
    if (risk.includes("High")) return "danger";
    if (risk.includes("Medium")) return "warning";
    return "success";
  };

  if (loading) return <Loader />;
  if (error) return <div className="page-wrapper">{error}</div>;

  return (
    <div className="page-wrapper">

      <h1>{userName} - Subject Risk Prediction</h1>

      {/* SEM FILTER */}
      <div style={{ marginBottom: "20px" }}>
        <select
          value={semester}
          onChange={(e) => setSemester(Number(e.target.value))}
        >
          {[...Array(8)].map((_, i) => (
            <option key={i} value={i + 1}>
              Sem {i + 1}
            </option>
          ))}
        </select>
      </div>

      {/* 🔥 TREND BUTTON */}
      <div style={{ marginBottom: "20px" }}>
        <button
          onClick={() => setShowTrend(prev => !prev)}
          style={{
            padding: "10px 15px",
            background: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer"
          }}
        >
          {showTrend ? "Hide Exam Trend Analysis" : "Show Exam Trend Analysis"}
        </button>
      </div>

      {/* 🔴 ONLY TREND CONTROLLED */}
      {showTrend && (
        <div style={{
          border: "2px solid #ddd",
          padding: "20px",
          marginBottom: "30px",
          borderRadius: "10px",
          background: "#f9f9f9"
        }}>
          <h2>Exam Trend Analysis</h2>

          <div className="dashboard-grid">
            {trendAnalysis.length === 0 ? (
              <p>No trend analysis available</p>
            ) : (
              trendAnalysis.map((trend, index) => (
                <div key={index} className="card">
                  <h3>{trend.subject}</h3>
                  <p><strong>MID:</strong> {trend.mid}</p>
                  <p><strong>Internal:</strong> {trend.internal}</p>
                  <p><strong>Final:</strong> {trend.final}</p>
                  <p><strong>Trend:</strong> {trend.trend}</p>
                  <p><strong>AI Insight:</strong><br />{trend.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* ✅ ALWAYS VISIBLE */}
      <h2>AI Recommendations</h2>
      <div className="card">
        {recommendations.length === 0 ? (
          <p>No recommendations available</p>
        ) : (
          <ul>
            {recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        )}
      </div>

      {/* ✅ ALWAYS VISIBLE */}
      <div className="dashboard-grid">
        {predictions.length === 0 ? (
          <p>No data found</p>
        ) : (
          predictions.map((item, index) => (
            <div key={index} className={`card ${getRiskClass(item.risk)}`}>
              <h3>{item.subject}</h3>
              <p><strong>Risk Level:</strong> {item.risk}</p>
              <p><strong>Attendance:</strong> {item.attendance}%</p>
              <p><strong>Average Marks:</strong> {item.average_marks}</p>
              <p><strong>AI Insight:</strong><br />{item.ai_insight}</p>
            </div>
          ))
        )}
      </div>

    </div>
  );
}