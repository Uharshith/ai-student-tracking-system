import { useEffect, useState } from "react";
import predictionService from "../../api/predictionService";
import Loader from "../../components/common/Loader";
import "../../styles/prediction.css";

export default function PredictionPage() {

  const userName = "AI";

  const [semester, setSemester] = useState(1);
  const [predictions, setPredictions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showTrend, setShowTrend] = useState(false);

  useEffect(() => {
    fetchPrediction();
  }, [semester]);

  const fetchPrediction = async () => {
    try {
      setLoading(true);

      const data = await predictionService.getSubjectRisk(semester);

      console.log("🔥 FINAL DATA:", data);

      setPredictions(data || []);

    } catch (err) {
      console.error("❌ Prediction Error:", err);
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

      {/* TREND BUTTON */}
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

      {/* TREND SECTION */}
      {showTrend && (
        <div className="dashboard-grid">
          {predictions.map((item, index) => (
            <div key={index} className="card">
              <h3>{item.subject}</h3>
              <p><strong>MID:</strong> {item.mid}</p>
              <p><strong>Internal:</strong> {item.internal}</p>
              <p><strong>Final:</strong> {item.final}</p>
              <p><strong>Trend:</strong> {item.trend}</p>
              <p><strong>AI Insight:</strong><br />{item.trend_message}</p>
            </div>
          ))}
        </div>
      )}

      {/* SUBJECT DATA */}
      <div className="dashboard-grid">
        {predictions.map((item, index) => (
          <div key={index} className={`card ${getRiskClass(item.risk)}`}>

            <h3>{item.subject}</h3>

            <p><strong>Risk:</strong> {item.risk}</p>
            <p><strong>Attendance:</strong> {item.attendance}%</p>
            <p><strong>Marks:</strong> {item.average_marks}</p>

            <p><strong>AI Insight:</strong><br />{item.ai_insight}</p>

            <p><strong>Recommendations:</strong></p>
            <ul>
              {item.recommendations.map((rec, i) => (
                <li key={i}>{rec}</li>
              ))}
            </ul>

          </div>
        ))}
      </div>

    </div>
  );
}