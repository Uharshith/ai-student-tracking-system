import { useEffect, useState } from "react";
import { getStudents } from "../../api/facultyService";
import Loader from "../../components/common/Loader";

export default function StudentsList() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const data = await getStudents();
        setStudents(data);
      } catch (error) {
        console.error("Students error:", error.response?.data || error);
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, []);

  if (loading) return <Loader />;

  return (
    <div className="page-wrapper">
      <h1>Students List</h1>

      {students.length === 0 ? (
        <p>No students found.</p>
      ) : (
        <table border="1" style={{ width: "100%", marginTop: "20px" }}>
          <thead>
            <tr>
              <th>Roll Number</th>
              <th>Name</th>
              <th>Year</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id}>
                <td>{student.roll_number}</td>
                <td>{student.name}</td>
                <td>{student.year}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}