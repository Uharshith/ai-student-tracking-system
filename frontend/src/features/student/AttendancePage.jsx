import { useEffect, useState } from "react";
import studentService from "../../api/studentService";
import "../../styles/dashboard.css";

export default function Attendance() {
  const [semester, setSemester] = useState(1);
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState("");

  const [records, setRecords] = useState([]);
  const [overall, setOverall] = useState(0);
  const [totalClasses, setTotalClasses] = useState(0);

  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [loadingData, setLoadingData] = useState(false);

  // ===============================
  // FETCH SUBJECTS (FIXED)
  // ===============================
  useEffect(() => {
    fetchSubjects();
  }, [semester]);

  const fetchSubjects = async () => {
    try {
      setLoadingSubjects(true);

      // ✅ CORRECT (number, not string)
      const res = await studentService.getSubjects(semester);

      setSubjects(res.data || []);

      // reset state
      setSelectedSubject("");
      setRecords([]);
      setOverall(0);
      setTotalClasses(0);

    } catch (err) {
      console.error("Error fetching subjects:", err);
    } finally {
      setLoadingSubjects(false);
    }
  };

  // ===============================
  // FETCH ATTENDANCE (FIXED)
  // ===============================
  useEffect(() => {
    if (!selectedSubject) return;

    fetchAttendance();
  }, [selectedSubject, semester]);

  const fetchAttendance = async () => {
    try {
      setLoadingData(true);

      // ✅ CORRECT (params object)
      const [summaryRes, historyRes] = await Promise.all([
        studentService.getAttendanceSummary({
          semester,
          subject_id: selectedSubject
        }),
        studentService.getAttendanceHistory({
          semester,
          subject_id: selectedSubject
        }),
      ]);

      setTotalClasses(summaryRes.data.total_classes || 0);
      setOverall(summaryRes.data.overall_percentage || 0);
      setRecords(historyRes.data || []);

    } catch (err) {
      console.error("Error fetching attendance:", err);
    } finally {
      setLoadingData(false);
    }
  };

  return (
    <div className="page-wrapper">
      <h1>Attendance Overview</h1>

      {/* ===============================
          FILTER SECTION
      =============================== */}
      <div style={{ marginBottom: "20px", display: "flex", gap: "10px" }}>

        {/* ✅ SEMESTER DROPDOWN */}
        <select
          value={semester}
          onChange={(e) => setSemester(Number(e.target.value))}
        >
          {[...Array(8)].map((_, i) => {
            const sem = i + 1;
            return (
              <option key={sem} value={sem}>
                Sem {sem}
              </option>
            );
          })}
        </select>

        {/* ✅ SUBJECT DROPDOWN */}
        {loadingSubjects ? (
          <span>Loading subjects...</span>
        ) : subjects.length === 0 ? (
          <span style={{ color: "red" }}>No subjects found</span>
        ) : (
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
          >
            <option value="">Select Subject</option>
            {subjects.map((sub) => (
              <option key={sub.id} value={sub.id}>
                {sub.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* ===============================
          DATA SECTION
      =============================== */}

      {!selectedSubject ? (
        <p>Select a subject to view attendance</p>
      ) : loadingData ? (
        <p>Loading attendance...</p>
      ) : (
        <>
          {/* SUMMARY */}
          <div className="summary-box">
            <div>
              <strong>Total Classes:</strong> {totalClasses}
            </div>
            <div>
              <strong>Overall Attendance:</strong> {overall}%
            </div>
          </div>

          {/* TABLE */}
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {records.length === 0 ? (
                  <tr>
                    <td colSpan="3" style={{ textAlign: "center" }}>
                      No data found
                    </td>
                  </tr>
                ) : (
                  records.map((item, index) => (
                    <tr key={index}>
                      <td>{item.subject}</td>
                      <td>{item.date}</td>
                      <td>
                        {item.status === "P" ? (
                          <span className="success">Present</span>
                        ) : (
                          <span className="danger">Absent</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}