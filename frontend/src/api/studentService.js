import api from "./axios";

const studentService = {

  // ================= PROFILE =================
  getProfile: () => api.get("/profile/"),

  updateProfile: (data) => api.put("/profile/", data),

  // ================= ATTENDANCE =================
  getAttendanceSummary: (params) => {
    return api.get("/student/attendance-summary/", { params });
  },

  getAttendanceHistory: (params) => {
    return api.get("/student/attendance-history/", { params });
  },

  // ================= MARKS =================
  getMarks: (semester) => {
    return api.get("/marks/my/", {
      params: { semester }
    });
  },

  // ================= SUBJECTS =================
  getSubjects: (semester) => {
    return api.get("/student/subjects/", {
      params: { semester }
    });
  },

  // ================= DASHBOARD =================
  getCurrentSemStats: () => {
    return api.get("/current-sem-dashboard/");
  },

  // 🔥 NEW — PIE CHART API
  getRiskPieChart: () => {
    return api.get("/subject-performance-pie/");
  },

};

export default studentService;