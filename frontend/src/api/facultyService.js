import axios from "./axios";

/* =========================
   SUBJECTS
========================= */

export const getSubjects = async () => {
  const response = await axios.get("/subjects/");
  return response.data;
};

/* =========================
   STUDENTS
========================= */

export const getStudentsBySubject = async (subjectId) => {
  const response = await axios.get(`/students/by-subject/${subjectId}/`);
  return response.data;
};

/* =========================
   ATTENDANCE
========================= */

export const createAttendance = async (data) => {
  const response = await axios.post("/attendance/create/", data);
  return response.data;
};

export const updateAttendance = async (id, data) => {
  const response = await axios.put(
    `/faculty/attendance/update/${id}/`,
    data
  );
  return response.data;
};

/* =========================
   MARKS
========================= */

export const createMarks = async (data) => {
  const response = await axios.post("/marks/create/", data);
  return response.data;
};

export const updateMarks = async (id, data) => {
  const response = await axios.put(
    `/faculty/marks/update/${id}/`,
    data
  );
  return response.data;
};

/* =========================
   PROFILE
========================= */

export const getFacultyProfile = async () => {
  const response = await axios.get("/profile/");
  return response.data;
};

export const getStudents = async () => {
  const response = await axios.get("/students/");
  return response.data;
};

export const getFacultyDashboard = async () => {
  const response = await axios.get("/faculty/dashboard/");
  return response.data;
};

export const getPerformanceTrend = async () => {
  const response = await axios.get("/faculty/performance-trend/");
  return response.data;
};
export const getSubjectBreakdown = async () => {
  const response = await axios.get("/faculty/subject-breakdown/");
  return response.data;
};

export const getFacultyRecommendations = async () => {
  const response = await axios.get("/faculty/recommendations/");
  return response.data;
};