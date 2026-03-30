import { Routes, Route, Navigate } from "react-router-dom";

import ProtectedRoute from "../components/common/ProtectedRoute";
import DashboardLayout from "../components/layout/DashboardLayout";

// Auth
import Auth from "../features/auth/Auth";

// Student
import StudentDashboard from "../features/student/StudentDashboard";
import AttendancePage from "../features/student/AttendancePage";
import MarksPage from "../features/student/MarksPage";
import PredictionPage from "../features/student/PredictionPage";
import ProfilePage from "../features/student/ProfilePage";

// Faculty
import FacultyDashboard from "../features/faculty/FacultyDashboard";
import AddAttendance from "../features/faculty/AddAttendance";
import AddMarks from "../features/faculty/AddMarks";
import StudentsList from "../features/faculty/StudentsList";
import FacultyRecommendations from "../features/faculty/FacultyRecommendations";

export default function AppRoutes() {
  return (
    <Routes>

      {/* Public Routes */}
      <Route path="/" element={<Auth />} />
      <Route path="/login" element={<Auth />} />
      <Route path="/register" element={<Auth />} />

      {/* Student Routes */}
      <Route
        path="/student"
        element={
          <ProtectedRoute role="STUDENT">
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="dashboard" />} />
        <Route path="dashboard" element={<StudentDashboard />} />
        <Route path="attendance" element={<AttendancePage />} />
        <Route path="marks" element={<MarksPage />} />
        <Route path="prediction" element={<PredictionPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>

      {/* Faculty Routes */}
      <Route
        path="/faculty"
        element={
          <ProtectedRoute role="FACULTY">
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="dashboard" />} />
        <Route path="dashboard" element={<FacultyDashboard />} />
        <Route path="add-attendance" element={<AddAttendance />} />
        <Route path="add-marks" element={<AddMarks />} />
        <Route path="students" element={<StudentsList />} />
        <Route path="recommendations" element={<FacultyRecommendations />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" />} />

    </Routes>
  );
}