import { NavLink } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <div className="sidebar">
      <h2 className="logo">AI Tracker</h2>

      {user?.role === "STUDENT" && (
        <>
          <NavLink to="/student/dashboard">Dashboard</NavLink>
          <NavLink to="/student/attendance">Attendance</NavLink>
          <NavLink to="/student/marks">Marks</NavLink>
          <NavLink to="/student/prediction">Prediction</NavLink>
          <NavLink to="/student/profile">Profile</NavLink>
        </>
      )}

      {user?.role === "FACULTY" && (
        <>
          <NavLink to="/faculty/dashboard">Dashboard</NavLink>
          <NavLink to="/faculty/students">Students</NavLink>
          <NavLink to="/faculty/add-attendance">Add Attendance</NavLink>
          <NavLink to="/faculty/add-marks">Add Marks</NavLink>
          <NavLink to="/faculty/recommendations">AI Recommendation</NavLink>
        </>
      )}
    </div>
  );
}