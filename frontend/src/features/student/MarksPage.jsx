import { useEffect, useState } from "react";
import studentService from "../../api/studentService";
import "../../styles/dashboard.css";

export default function Marks() {
  const [semester, setSemester] = useState(1);
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState("");
  const [examType, setExamType] = useState("");

  const [marks, setMarks] = useState([]);
  const [filteredMarks, setFilteredMarks] = useState([]);
  const [average, setAverage] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ================= FETCH SUBJECTS =================
  useEffect(() => {
    fetchSubjects();
  }, [semester]);

  const fetchSubjects = async () => {
    try {
      const res = await studentService.getSubjects(semester);
      setSubjects(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  // ================= FETCH MARKS =================
  useEffect(() => {
    fetchMarks();
  }, [semester]);

  const fetchMarks = async () => {
    try {
      setLoading(true);

      const res = await studentService.getMarks(semester);

      const data =
        res.data?.data ||
        res.data?.results ||
        res.data ||
        [];

      if (!Array.isArray(data)) {
        throw new Error("Invalid marks data format");
      }

      setMarks(data);
      setFilteredMarks(data);
      calculateAverage(data);

    } catch (err) {
      console.error(err);
      setError("Failed to load marks data");
    } finally {
      setLoading(false);
    }
  };

  // ================= FILTER LOGIC =================
  const applyFilters = () => {
    let data = [...marks];

    // Subject filter
    if (selectedSubject) {
      const subjectName = subjects.find(
        (s) => s.id == selectedSubject
      )?.name;

      data = data.filter((m) => m.subject === subjectName);
    }

    // Exam type filter
    if (examType) {
      data = data.filter((m) => m.exam_type === examType);
    }

    setFilteredMarks(data);
    calculateAverage(data);
  };

  // ================= AVERAGE =================
  const calculateAverage = (data) => {
    if (data.length === 0) {
      setAverage(0);
      return;
    }

    const total = data.reduce(
      (sum, item) => sum + Number(item.marks_obtained || 0),
      0
    );

    setAverage((total / data.length).toFixed(2));
  };

  // ================= GRADE =================
  const getGrade = (value) => {
    if (value >= 85) return { label: "A+", className: "success" };
    if (value >= 75) return { label: "A", className: "success" };
    if (value >= 60) return { label: "B", className: "warning" };
    return { label: "C", className: "danger" };
  };

  if (loading) return <div className="page-wrapper">Loading...</div>;
  if (error) return <div className="page-wrapper">{error}</div>;

  return (
    <div className="page-wrapper">
      <h1>Marks Overview</h1>
      <p className="page-subtitle">
        Review your academic performance by subject
      </p>

      {/* ================= FILTERS ================= */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>

        {/* SEMESTER */}
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

        {/* SUBJECT */}
        <select
          value={selectedSubject}
          onChange={(e) => setSelectedSubject(e.target.value)}
        >
          <option value="">All Subjects</option>
          {subjects.map((sub) => (
            <option key={sub.id} value={sub.id}>
              {sub.name}
            </option>
          ))}
        </select>

        {/* EXAM TYPE */}
        <select
          value={examType}
          onChange={(e) => setExamType(e.target.value)}
        >
          <option value="">All Exams</option>
          <option value="MID">MID</option>
          <option value="INT">INT</option>
          <option value="FIN">FIN</option>
        </select>

        {/* APPLY BUTTON */}
        <button onClick={applyFilters}>Apply</button>
      </div>

      {/* ================= SUMMARY ================= */}
      <div className="summary-box">
        <div>
          <strong>Total Records:</strong> {filteredMarks.length}
        </div>
        <div>
          <strong>Average Marks:</strong> {average}
        </div>
      </div>

      {/* ================= TABLE ================= */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Subject</th>
              <th>Exam Type</th>
              <th>Marks</th>
              <th>Grade</th>
            </tr>
          </thead>
          <tbody>
            {filteredMarks.length === 0 ? (
              <tr>
                <td colSpan="4" style={{ textAlign: "center" }}>
                  No marks records found
                </td>
              </tr>
            ) : (
              filteredMarks.map((item, index) => {
                const value = Number(item.marks_obtained || 0);
                const grade = getGrade(value);

                return (
                  <tr key={index}>
                    <td>{item.subject}</td>
                    <td>{item.exam_type}</td>
                    <td>{value}</td>
                    <td>
                      <span className={grade.className}>
                        {grade.label}
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}