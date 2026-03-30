import api from "./axios";

const studentService = {

  // ================= PROFILE =================
  getProfile: () => api.get("/profile/"),

  updateProfile: (data) => api.put("/profile/", data),

  // ================= ATTENDANCE =================

  // ✅ CLEAN PARAMS (NO STRING CONCAT BUGS)
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

  // ================= RECOMMENDATION =================
  getRecommendation: () => api.get("/recommendation/"),
};

export default studentService;