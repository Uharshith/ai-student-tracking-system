import { useEffect, useState } from "react";
import {
  getSubjects,
  getStudentsBySubject,
  createMarks,
} from "../../api/facultyService";
import Loader from "../../components/common/Loader";

export default function AddMarks() {
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [subjectId, setSubjectId] = useState("");
  const [examType, setExamType] = useState("");
  const [marksData, setMarksData] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Load subjects
  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const data = await getSubjects();
        setSubjects(data);
      } catch (error) {
        console.error("Subjects error:", error.response?.data || error);

        if (error.response?.status === 401) {
          alert("Session expired. Please login again.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchSubjects();
  }, []);

  // Load students when subject changes
  useEffect(() => {
    if (!subjectId) {
      setStudents([]);
      return;
    }

    const fetchStudents = async () => {
      try {
        const data = await getStudentsBySubject(subjectId);
        setStudents(data);

        const initial = {};
        data.forEach((student) => {
          initial[student.id] = "";
        });
        setMarksData(initial);
      } catch (error) {
        console.error("Students error:", error.response?.data || error);
      }
    };

    fetchStudents();
  }, [subjectId]);

  const handleMarksChange = (studentId, value) => {
    if (value < 0) return;

    setMarksData((prev) => ({
      ...prev,
      [studentId]: value,
    }));
  };

  const handleSubmit = async () => {
    if (!subjectId) {
      alert("Select subject");
      return;
    }

    if (!examType) {
      alert("Select exam type");
      return;
    }

    try {
      setSubmitting(true);

      for (let student of students) {
        const marks = marksData[student.id];

        if (marks === "" || marks === undefined) continue;

        await createMarks({
          student: student.id,
          subject: Number(subjectId),
          exam_type: examType,
          marks_obtained: Number(marks),
        });
      }

      alert("Marks submitted successfully");

      // reset after submit
      setStudents([]);
      setSubjectId("");
      setExamType("");
      setMarksData({});
    } catch (error) {
      console.error("Submit error:", error.response?.data || error);
      alert("Error submitting marks");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="page-wrapper">
      <h1>Add Marks</h1>

      {/* Subject Dropdown */}
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

      {/* Exam Type */}
      <div style={{ marginTop: "10px" }}>
        <label>Select Exam Type</label>
        <select
          value={examType}
          onChange={(e) => setExamType(e.target.value)}
        >
          <option value="">Select Exam</option>
          <option value="MID">Midterm</option>
          <option value="INT">Internal</option>
          <option value="FIN">Final</option>
        </select>
      </div>

      {/* Students Table */}
      {students.length > 0 && (
        <>
          <table style={{ marginTop: "20px", width: "100%" }} border="1">
            <thead>
              <tr>
                <th>Roll No</th>
                <th>Name</th>
                <th>Marks</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td>{student.roll_number}</td>
                  <td>{student.name}</td>
                  <td>
                    <input
                      type="number"
                      value={marksData[student.id] || ""}
                      onChange={(e) =>
                        handleMarksChange(student.id, e.target.value)
                      }
                      placeholder="Enter marks"
                    />
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
            {submitting ? "Submitting..." : "Submit Marks"}
          </button>
        </>
      )}
    </div>
  );
}