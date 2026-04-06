from django.urls import path
from .views import (
    AttendanceCreateView,
    MarksCreateView,
    StudentMarksView,
    AttendanceUpdateView,
    MarksUpdateView,
    LoginAPIView,
    StudentRegisterAPIView,
    FacultyRegisterAPIView,
    ProfileAPIView,
    SubjectListAPIView, SubjectCreateView,
    StudentsBySubjectAPIView,
    FacultyStudentsListAPIView,
    FacultyDashboardAPIView,
    FacultyPerformanceTrendAPIView,
    FacultySubjectBreakdownAPIView,
    FacultyRecommendationAPIView,
    BulkStudentRegisterView,
    StudentAttendanceHistoryView,
    StudentAttendanceSummaryView,
    SubjectRiskPredictionView,
    StudentSubjectListAPIView,
    StudentDashboardAPIView,
    SemesterPerformancePieAPIView,
)

urlpatterns = [

    # ===============================
    # AUTH
    # ===============================
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("register/student/", StudentRegisterAPIView.as_view(), name="student-register"),
    path("register/faculty/", FacultyRegisterAPIView.as_view(), name="faculty-register"),

    # ===============================
    # ATTENDANCE
    # ===============================
    path("attendance/create/", AttendanceCreateView.as_view(), name="attendance-create"),
   
    path("faculty/attendance/update/<int:pk>/", AttendanceUpdateView.as_view(), name="attendance-update"),

    # ===============================
    # MARKS
    # ===============================
    path("marks/create/", MarksCreateView.as_view(), name="marks-create"),
    path("marks/my/", StudentMarksView.as_view(), name="marks-my"),
    path("faculty/marks/update/<int:pk>/", MarksUpdateView.as_view(), name="marks-update"),

    # ===============================
    # AI RECOMMENDATION
    # ===============================
    path("profile/", ProfileAPIView.as_view(), name="profile"),

     path("subjects/", SubjectListAPIView.as_view(), name="subjects-list"),
    path("subjects/create/", SubjectCreateView.as_view(), name="subjects-create"),

    path("students/by-subject/<int:subject_id>/", StudentsBySubjectAPIView.as_view()),
    path("students/", FacultyStudentsListAPIView.as_view()),
    # urls.py

path("faculty/dashboard/", FacultyDashboardAPIView.as_view()),
path("faculty/performance-trend/", FacultyPerformanceTrendAPIView.as_view()),

path("faculty/subject-breakdown/", FacultySubjectBreakdownAPIView.as_view()),

path("faculty/recommendations/", FacultyRecommendationAPIView.as_view()),
path("bulk-register-students/", BulkStudentRegisterView.as_view()),

path("student/attendance-summary/", StudentAttendanceSummaryView.as_view()),
path("student/attendance-history/", StudentAttendanceHistoryView.as_view()),
path("subject-risk/", SubjectRiskPredictionView.as_view()),
path("student/subjects/", StudentSubjectListAPIView.as_view()),
 path("current-sem-dashboard/", StudentDashboardAPIView.as_view()),
 path("subject-performance-pie/", SemesterPerformancePieAPIView.as_view()),
]