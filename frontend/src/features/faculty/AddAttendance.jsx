import { useEffect, useState } from "react";
import {
  getSubjects,
  getStudentsBySubject,
  createAttendance,
} from "../../api/facultyService";
import Loader from "../../components/common/Loader";

export default function AddAttendance() {
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [subjectId, setSubjectId] = useState("");
  const [date] = useState(new Date().toISOString().split("T")[0]);
  const [attendanceData, setAttendanceData] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Load subjects
  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const data = await getSubjects();
        setSubjects(data);
      } catch (error) {
        console.error("Subjects error:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSubjects();
  }, []);

  // Load students when subject changes
  useEffect(() => {
    if (!subjectId) return;

    const fetchStudents = async () => {
      try {
        const data = await getStudentsBySubject(subjectId);
        setStudents(data);

        // Initialize attendance state (default Absent)
        const initial = {};
        data.forEach((student) => {
          initial[student.id] = "A";
        });
        setAttendanceData(initial);
      } catch (error) {
        console.error("Students error:", error);
      }
    };

    fetchStudents();
  }, [subjectId]);

  const handleStatusChange = (studentId, status) => {
    setAttendanceData((prev) => ({
      ...prev,
      [studentId]: status,
    }));
  };

  const handleSubmit = async () => {
    if (!subjectId || students.length === 0) return;

    try {
      setSubmitting(true);

      for (let student of students) {
        await createAttendance({
          student: student.id,
          subject: subjectId,
          date: date,
          status: attendanceData[student.id],
        });
      }

      alert("Attendance submitted successfully");
    } catch (error) {
      console.error("Submit error:", error.response?.data || error);
      alert("Error submitting attendance");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="page-wrapper">
      <h1>Add Attendance</h1>

      {/* Subject Selection */}
      <div>
        <label>Select Subject</label>
        <select
          value={subjectId}
          onChange={(e) => setSubjectId(e.target.value)}
        >
          <option value="">Select Subject</option>
          {subjects.map((subject) => (
            <option key={subject.id} value={subject.id}>
              {subject.name} - Year {subject.year}
            </option>
          ))}
        </select>
      </div>

      {/* Students Table */}
      {students.length > 0 && (
        <>
          <table border="1" style={{ marginTop: "20px", width: "100%" }}>
            <thead>
              <tr>
                <th>Roll No</th>
                <th>Name</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td>{student.roll_number}</td>
                  <td>{student.name}</td>
                  <td>
                    <select
                      value={attendanceData[student.id]}
                      onChange={(e) =>
                        handleStatusChange(student.id, e.target.value)
                      }
                    >
                      <option value="P">Present</option>
                      <option value="A">Absent</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <button
            onClick={handleSubmit}
            disabled={submitting}
            style={{ marginTop: "20px" }}
          >
            {submitting ? "Submitting..." : "Submit Attendance"}
          </button>
        </>
      )}
    </div>
  );
}