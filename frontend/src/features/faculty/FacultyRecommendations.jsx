import { useEffect, useState } from "react";
import { getFacultyRecommendations } from "../../api/facultyService";
import Loader from "../../components/common/Loader";

export default function FacultyRecommendations() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getFacultyRecommendations();
        setData(res);
      } catch (error) {
        console.error(error.response?.data || error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <Loader />;

  return (
    <div className="page-wrapper">
      <h1>AI Risk Analysis</h1>

      <table border="1" style={{ width: "100%", marginTop: "20px" }}>
        <thead>
          <tr>
            <th>Roll</th>
            <th>Name</th>
            <th>Avg Marks</th>
            <th>Attendance %</th>
            <th>Risk Level</th>
          </tr>
        </thead>
        <tbody>
          {data.map((student, index) => (
            <tr key={index}>
              <td>{student.roll_number}</td>
              <td>{student.student}</td>
              <td>{student.avg_marks}</td>
              <td>{student.attendance}%</td>
              <td>{student.risk}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}