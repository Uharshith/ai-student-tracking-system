from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Avg

from .models import (
    Subject,
    Attendance,
    Marks,
    Student,
    Faculty,
    Profile
)
from .serializers import (
    SubjectSerializer,
    AttendanceSerializer,
    MarksSerializer
)
from .permissions import IsFaculty, IsStudent

from ml_engine.predict import predict_performance
from ml_engine.recommender import generate_recommendation


# =====================================================
# AUTHENTICATION
# =====================================================

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not hasattr(user, "profile"):
            return Response(
                {"detail": "Profile not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.profile.role
            }
        }, status=status.HTTP_200_OK)


class StudentRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        name = request.data.get("name")
        roll_number = request.data.get("roll_number")
        department = request.data.get("department")
        year = request.data.get("year")

        if not all([username, password, name, roll_number, department, year]):
            return Response({"detail": "All fields are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists"}, status=400)

        if Student.objects.filter(roll_number=roll_number).exists():
            return Response({"detail": "Roll number already exists"}, status=400)

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )

        Profile.objects.create(user=user, role="STUDENT")

        Student.objects.create(
            user=user,
            name=name,
            roll_number=roll_number,
            department=department,
            year=year
        )

        return Response(
            {"message": "Student registered successfully"},
            status=status.HTTP_201_CREATED
        )


class FacultyRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        name = request.data.get("name")
        department = request.data.get("department")
        designation = request.data.get("designation")

        if not all([username, password, name, department, designation]):
            return Response({"detail": "All fields are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists"}, status=400)

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )

        Profile.objects.create(user=user, role="FACULTY")

        Faculty.objects.create(
            user=user,
            name=name,
            department=department,
            designation=designation
        )

        return Response(
            {"message": "Faculty registered successfully"},
            status=status.HTTP_201_CREATED
        )


# =====================================================
# SUBJECT & ACADEMIC MANAGEMENT
# =====================================================

class SubjectCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class SubjectListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        subjects = Subject.objects.filter(
            department=request.user.faculty.department
        )
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)



class AttendanceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def post(self, request):
        serializer = AttendanceSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AttendanceUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def put(self, request, pk):
        try:
            attendance = Attendance.objects.get(id=pk)
        except Attendance.DoesNotExist:
            return Response({"detail": "Attendance not found"}, status=404)

        serializer = AttendanceSerializer(
            attendance,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)



from django.db import transaction

class MarksCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    @transaction.atomic
    def post(self, request):
        student = request.data.get("student")
        subject = request.data.get("subject")
        exam_type = request.data.get("exam_type")
        marks = request.data.get("marks_obtained")

        obj, created = Marks.objects.update_or_create(
            student_id=student,
            subject_id=subject,
            exam_type=exam_type,
            defaults={
                "marks_obtained": marks,
                "entered_by": request.user.faculty,
            }
        )

        return Response({
            "message": "Created" if created else "Updated"
        })

class MarksUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def put(self, request, pk):
        try:
            marks = Marks.objects.get(id=pk)
        except Marks.DoesNotExist:
            return Response({"detail": "Marks record not found"}, status=404)

        serializer = MarksSerializer(
            marks,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class StudentMarksView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found"}, status=400)

        marks = Marks.objects.filter(student=student)
        serializer = MarksSerializer(marks, many=True)
        return Response(serializer.data)


# =====================================================
# AI RECOMMENDATION ENGINE
# =====================================================

class RecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not hasattr(request.user, "profile"):
            return Response({"detail": "Profile not found"}, status=400)

        role = request.user.profile.role

        if role == "STUDENT":

            try:
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                return Response({"detail": "Student profile not found"}, status=400)

            total_classes = Attendance.objects.filter(student=student).count()
            present_classes = Attendance.objects.filter(
                student=student,
                status='P'
            ).count()

            attendance_percentage = (
                (present_classes / total_classes) * 100
                if total_classes > 0 else 0
            )

            avg_marks = Marks.objects.filter(student=student).aggregate(
                average=Avg("marks_obtained")
            )["average"] or 0

            backlog_count = Marks.objects.filter(
                student=student,
                marks_obtained__lt=40
            ).count()

            prediction = predict_performance(
                attendance_percentage,
                avg_marks,
                avg_marks,
                backlog_count
            )

            result = generate_recommendation(prediction)

            return Response({
                "attendance_percentage": round(attendance_percentage, 2),
                "average_marks": round(avg_marks, 2),
                "backlogs": backlog_count,
                "performance_level": result["performance_level"],
                "risk_level": result["risk_level"],
                "recommendations": result["student_recommendations"]
            })

        elif role == "FACULTY":

            students = Student.objects.all()
            summary = {"High": 0, "Medium": 0, "Low": 0}

            for student in students:
                total_classes = Attendance.objects.filter(student=student).count()
                present_classes = Attendance.objects.filter(
                    student=student,
                    status='P'
                ).count()

                attendance_percentage = (
                    (present_classes / total_classes) * 100
                    if total_classes > 0 else 0
                )

                avg_marks = Marks.objects.filter(student=student).aggregate(
                    average=Avg("marks_obtained")
                )["average"] or 0

                backlog_count = Marks.objects.filter(
                    student=student,
                    marks_obtained__lt=40
                ).count()

                prediction = predict_performance(
                    attendance_percentage,
                    avg_marks,
                    avg_marks,
                    backlog_count
                )

                result = generate_recommendation(prediction)
                summary[result["performance_level"]] += 1

            return Response({"category_summary": summary})

        return Response({"detail": "Invalid role"}, status=400)
    
from rest_framework.permissions import IsAuthenticated

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # ================= GET PROFILE =================
    def get(self, request):
        user = request.user

        if not hasattr(user, "profile"):
            return Response({"detail": "Profile not found"}, status=400)

        role = user.profile.role

        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,  # ✅ include email
            "role": role,
        }

        if role == "STUDENT":
            try:
                student = Student.objects.get(user=user)
                data.update({
                    "name": student.name,
                    "roll_number": student.roll_number,
                    "department": student.department,
                    "year": student.year,
                })
            except Student.DoesNotExist:
                return Response({"detail": "Student data not found"}, status=400)

        elif role == "FACULTY":
            try:
                faculty = Faculty.objects.get(user=user)
                data.update({
                    "name": faculty.name,
                    "department": faculty.department,
                    "designation": faculty.designation,
                })
            except Faculty.DoesNotExist:
                return Response({"detail": "Faculty data not found"}, status=400)

        return Response(data)

    # ================= UPDATE PROFILE =================
    def put(self, request):
        user = request.user

        if not hasattr(user, "profile"):
            return Response({"detail": "Profile not found"}, status=400)

        role = user.profile.role

        if role == "STUDENT":
            try:
                student = Student.objects.get(user=user)

                # Only department & year editable
                department = request.data.get("department")
                year = request.data.get("year")

                if department:
                    student.department = department

                if year:
                    student.year = year

                student.save()

                return Response({
                    "message": "Profile updated successfully",
                    "department": student.department,
                    "year": student.year,
                })

            except Student.DoesNotExist:
                return Response({"detail": "Student data not found"}, status=400)

        elif role == "FACULTY":
            try:
                faculty = Faculty.objects.get(user=user)

                # Faculty can update department & designation
                department = request.data.get("department")
                designation = request.data.get("designation")

                if department:
                    faculty.department = department

                if designation:
                    faculty.designation = designation

                faculty.save()

                return Response({
                    "message": "Profile updated successfully",
                    "department": faculty.department,
                    "designation": faculty.designation,
                })

            except Faculty.DoesNotExist:
                return Response({"detail": "Faculty data not found"}, status=400)

        return Response({"detail": "Invalid role"}, status=400)
    

from .models import Student, Subject
from rest_framework.permissions import IsAuthenticated
from .permissions import IsFaculty
from rest_framework.views import APIView
from rest_framework.response import Response

class StudentsBySubjectAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=404)

        students = Student.objects.filter(
            department=subject.department,
            year=subject.year,
            is_active=True
        )

        data = [
            {
                "id": student.id,
                "name": student.name,
                "roll_number": student.roll_number
            }
            for student in students
        ]

        return Response(data)
    
class FacultyStudentsListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        students = Student.objects.filter(
            department=request.user.faculty.department,
            is_active=True
        )

        data = [
            {
                "id": s.id,
                "name": s.name,
                "roll_number": s.roll_number,
                "year": s.year
            }
            for s in students
        ]

        return Response(data)
    
# views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Student, Attendance, Marks
from .permissions import IsFaculty


class FacultyDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        faculty = request.user.faculty
        department = faculty.department

        # Total students
        total_students = Student.objects.filter(
            department=department,
            is_active=True
        ).count()

        # Average marks
        avg_marks = Marks.objects.filter(
            student__department=department
        ).aggregate(avg=Avg("marks_obtained"))["avg"]

        avg_marks = round(avg_marks, 2) if avg_marks else 0

        # Attendance %
        total_attendance = Attendance.objects.filter(
            student__department=department
        ).count()

        present_attendance = Attendance.objects.filter(
            student__department=department,
            status="P"
        ).count()

        attendance_percentage = (
            round((present_attendance / total_attendance) * 100, 2)
            if total_attendance > 0 else 0
        )

        # At risk students (marks < 40)
        at_risk_students = Marks.objects.filter(
            student__department=department,
            marks_obtained__lt=40
        ).values("student").distinct().count()

        return Response({
            "total_students": total_students,
            "attendance_percentage": attendance_percentage,
            "average_marks": avg_marks,
            "at_risk_students": at_risk_students
        })
# views.py

from django.db.models.functions import TruncMonth
from django.db.models import Avg
from collections import defaultdict


class FacultyPerformanceTrendAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        department = request.user.faculty.department

        data = (
            Marks.objects.filter(student__department=department)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(avg_marks=Avg("marks_obtained"))
            .order_by("month")
        )

        return Response(data)

from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Marks
from .permissions import IsFaculty


class FacultySubjectBreakdownAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        department = request.user.faculty.department

        data = (
            Marks.objects.filter(student__department=department)
            .values("subject__name")
            .annotate(avg_marks=Avg("marks_obtained"))
            .order_by("subject__name")
        )

        formatted = [
            {
                "subject": item["subject__name"],
                "avg_marks": round(item["avg_marks"], 2)
            }
            for item in data
        ]

        return Response(formatted)

from django.db.models import Avg, Count, Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Student, Marks, Attendance
from .permissions import IsFaculty


class FacultyRecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        department = request.user.faculty.department

        students = Student.objects.filter(department=department)

        results = []

        for student in students:
            avg_marks = (
                Marks.objects.filter(student=student)
                .aggregate(avg=Avg("marks_obtained"))["avg"] or 0
            )

            total_days = Attendance.objects.filter(student=student).count()
            present_days = Attendance.objects.filter(
                student=student, status="P"
            ).count()

            attendance_percentage = (
                (present_days / total_days) * 100 if total_days > 0 else 0
            )

            risk_level = "Low"

            if avg_marks < 40 or attendance_percentage < 60:
                risk_level = "High"
            elif avg_marks < 50 or attendance_percentage < 70:
                risk_level = "Medium"

            results.append({
                "student": student.name,
                "roll_number": student.roll_number,
                "avg_marks": round(avg_marks, 2),
                "attendance": round(attendance_percentage, 2),
                "risk": risk_level
            })

        return Response(results)

import pandas as pd
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Profile


class BulkStudentRegisterView(APIView):

    @transaction.atomic
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        df = pd.read_excel(file)

        created_count = 0
        skipped_count = 0

        # 125 students per year
        year_distribution = [1]*125 + [2]*125 + [3]*125 + [4]*125

        for index, (_, row) in enumerate(df.iterrows()):
            roll = str(row["roll_number"]).strip()

            if User.objects.filter(username=roll).exists():
                skipped_count += 1
                continue

            assigned_year = year_distribution[index]

            # Create User
            user = User.objects.create_user(
                username=roll,
                password=roll
            )

            # Create Profile
            Profile.objects.create(
                user=user,
                role="STUDENT"
            )

            # Create Student
            Student.objects.create(
                user=user,
                name=roll,
                roll_number=roll,
                department="CSE",
                year=assigned_year
            )

            created_count += 1

        return Response(
            {
                "created": created_count,
                "skipped_existing": skipped_count
            },
            status=status.HTTP_201_CREATED
        )
 
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Avg

from .models import (
    Subject,
    Attendance,
    Marks,
    Student,
    Faculty,
    Profile
)
from .serializers import (
    SubjectSerializer,
    AttendanceSerializer,
    MarksSerializer
)
from .permissions import IsFaculty, IsStudent

from ml_engine.predict import predict_performance
from ml_engine.recommender import generate_recommendation


# =====================================================
# AUTHENTICATION
# =====================================================

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not hasattr(user, "profile"):
            return Response(
                {"detail": "Profile not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.profile.role
            }
        }, status=status.HTTP_200_OK)


class StudentRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        name = request.data.get("name")
        roll_number = request.data.get("roll_number")
        department = request.data.get("department")
        year = request.data.get("year")

        if not all([username, password, name, roll_number, department, year]):
            return Response({"detail": "All fields are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists"}, status=400)

        if Student.objects.filter(roll_number=roll_number).exists():
            return Response({"detail": "Roll number already exists"}, status=400)

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )

        Profile.objects.create(user=user, role="STUDENT")

        Student.objects.create(
            user=user,
            name=name,
            roll_number=roll_number,
            department=department,
            year=year
        )

        return Response(
            {"message": "Student registered successfully"},
            status=status.HTTP_201_CREATED
        )


class FacultyRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        name = request.data.get("name")
        department = request.data.get("department")
        designation = request.data.get("designation")

        if not all([username, password, name, department, designation]):
            return Response({"detail": "All fields are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists"}, status=400)

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )

        Profile.objects.create(user=user, role="FACULTY")

        Faculty.objects.create(
            user=user,
            name=name,
            department=department,
            designation=designation
        )

        return Response(
            {"message": "Faculty registered successfully"},
            status=status.HTTP_201_CREATED
        )


# =====================================================
# SUBJECT & ACADEMIC MANAGEMENT
# =====================================================

class SubjectCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class SubjectListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        semester = request.GET.get("semester")
        year = request.GET.get("year")

        subjects = Subject.objects.filter(
            department=request.user.faculty.department,
            semester=semester,
            year=year
        )

        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

class AttendanceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def post(self, request):
        serializer = AttendanceSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AttendanceUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def put(self, request, pk):
        try:
            attendance = Attendance.objects.get(id=pk)
        except Attendance.DoesNotExist:
            return Response({"detail": "Attendance not found"}, status=404)

        serializer = AttendanceSerializer(
            attendance,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)



from django.db import transaction

class MarksCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    @transaction.atomic
    def post(self, request):
        student = request.data.get("student")
        subject = request.data.get("subject")
        exam_type = request.data.get("exam_type")
        marks = request.data.get("marks_obtained")

        obj, created = Marks.objects.update_or_create(
            student_id=student,
            subject_id=subject,
            exam_type=exam_type,
            defaults={
                "marks_obtained": marks,
                "entered_by": request.user.faculty,
            }
        )

        return Response({
            "message": "Created" if created else "Updated"
        })

class MarksUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def put(self, request, pk):
        try:
            marks = Marks.objects.get(id=pk)
        except Marks.DoesNotExist:
            return Response({"detail": "Marks record not found"}, status=404)

        serializer = MarksSerializer(
            marks,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class StudentMarksView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found"}, status=400)

        marks = Marks.objects.filter(student=student)
        serializer = MarksSerializer(marks, many=True)
        return Response(serializer.data)


# =====================================================
# AI RECOMMENDATION ENGINE
# =====================================================

class RecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not hasattr(request.user, "profile"):
            return Response({"detail": "Profile not found"}, status=400)

        role = request.user.profile.role

        # ===============================
        # 🔥 GET SEMESTER (NEW)
        # ===============================
        semester = request.GET.get("semester")

        try:
            semester = int(semester) if semester else None
        except ValueError:
            return Response({"error": "Invalid semester"}, status=400)

        print("SEM:", semester)

        # =====================================================
        # STUDENT
        # =====================================================
        if role == "STUDENT":

            try:
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                return Response({"detail": "Student profile not found"}, status=400)

            # ===============================
            # 🔥 APPLY FILTER (MAIN FIX)
            # ===============================
            attendance_qs = Attendance.objects.filter(student=student)
            marks_qs = Marks.objects.filter(student=student)

            if semester:
                attendance_qs = attendance_qs.filter(subject__semester=semester)
                marks_qs = marks_qs.filter(subject__semester=semester)

            # ===============================
            # ATTENDANCE
            # ===============================
            total_classes = attendance_qs.count()
            present_classes = attendance_qs.filter(status='P').count()

            attendance_percentage = (
                (present_classes / total_classes) * 100
                if total_classes > 0 else 0
            )

            # ===============================
            # MARKS
            # ===============================
            avg_marks = marks_qs.aggregate(
                average=Avg("marks_obtained")
            )["average"] or 0

            backlog_count = marks_qs.filter(
                marks_obtained__lt=40
            ).count()

            # ===============================
            # PREDICTION
            # ===============================
            prediction = predict_performance(
                attendance_percentage,
                avg_marks,
                avg_marks,
                backlog_count
            )

            result = generate_recommendation(prediction)

            return Response({
                "attendance_percentage": round(attendance_percentage, 2),
                "average_marks": round(avg_marks, 2),
                "backlogs": backlog_count,
                "performance_level": result["performance_level"],
                "risk_level": result["risk_level"],
                "recommendations": result["student_recommendations"]
            })

        # =====================================================
        # FACULTY
        # =====================================================
        elif role == "FACULTY":

            students = Student.objects.all()
            summary = {"High": 0, "Medium": 0, "Low": 0}

            for student in students:

                attendance_qs = Attendance.objects.filter(student=student)
                marks_qs = Marks.objects.filter(student=student)

                if semester:
                    attendance_qs = attendance_qs.filter(subject__semester=semester)
                    marks_qs = marks_qs.filter(subject__semester=semester)

                total_classes = attendance_qs.count()
                present_classes = attendance_qs.filter(status='P').count()

                attendance_percentage = (
                    (present_classes / total_classes) * 100
                    if total_classes > 0 else 0
                )

                avg_marks = marks_qs.aggregate(
                    average=Avg("marks_obtained")
                )["average"] or 0

                backlog_count = marks_qs.filter(
                    marks_obtained__lt=40
                ).count()

                prediction = predict_performance(
                    attendance_percentage,
                    avg_marks,
                    avg_marks,
                    backlog_count
                )

                result = generate_recommendation(prediction)
                summary[result["performance_level"]] += 1

            return Response({"category_summary": summary})

        return Response({"detail": "Invalid role"}, status=400)
    
    
from rest_framework.permissions import IsAuthenticated

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # ================= GET PROFILE =================
    def get(self, request):
        user = request.user

        if not hasattr(user, "profile"):
            return Response({"detail": "Profile not found"}, status=400)

        role = user.profile.role

        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,  # ✅ include email
            "role": role,
        }

        if role == "STUDENT":
            try:
                student = Student.objects.get(user=user)
                data.update({
                    "name": student.name,
                    "roll_number": student.roll_number,
                    "department": student.department,
                    "year": student.year,
                })
            except Student.DoesNotExist:
                return Response({"detail": "Student data not found"}, status=400)

        elif role == "FACULTY":
            try:
                faculty = Faculty.objects.get(user=user)
                data.update({
                    "name": faculty.name,
                    "department": faculty.department,
                    "designation": faculty.designation,
                })
            except Faculty.DoesNotExist:
                return Response({"detail": "Faculty data not found"}, status=400)

        return Response(data)

    # ================= UPDATE PROFILE =================
    def put(self, request):
        user = request.user

        if not hasattr(user, "profile"):
            return Response({"detail": "Profile not found"}, status=400)

        role = user.profile.role

        if role == "STUDENT":
            try:
                student = Student.objects.get(user=user)

                # Only department & year editable
                department = request.data.get("department")
                year = request.data.get("year")

                if department:
                    student.department = department

                if year:
                    student.year = year

                student.save()

                return Response({
                    "message": "Profile updated successfully",
                    "department": student.department,
                    "year": student.year,
                })

            except Student.DoesNotExist:
                return Response({"detail": "Student data not found"}, status=400)

        elif role == "FACULTY":
            try:
                faculty = Faculty.objects.get(user=user)

                # Faculty can update department & designation
                department = request.data.get("department")
                designation = request.data.get("designation")

                if department:
                    faculty.department = department

                if designation:
                    faculty.designation = designation

                faculty.save()

                return Response({
                    "message": "Profile updated successfully",
                    "department": faculty.department,
                    "designation": faculty.designation,
                })

            except Faculty.DoesNotExist:
                return Response({"detail": "Faculty data not found"}, status=400)

        return Response({"detail": "Invalid role"}, status=400)
    

from .models import Student, Subject
from rest_framework.permissions import IsAuthenticated
from .permissions import IsFaculty
from rest_framework.views import APIView
from rest_framework.response import Response

class StudentsBySubjectAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=404)

        students = Student.objects.filter(
            department=subject.department,
            year=subject.year,
            is_active=True
        )

        data = [
            {
                "id": student.id,
                "name": student.name,
                "roll_number": student.roll_number
            }
            for student in students
        ]

        return Response(data)
    
class FacultyStudentsListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        students = Student.objects.filter(
            department=request.user.faculty.department,
            is_active=True
        )

        data = [
            {
                "id": s.id,
                "name": s.name,
                "roll_number": s.roll_number,
                "year": s.year
            }
            for s in students
        ]

        return Response(data)
    
# views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Student, Attendance, Marks
from .permissions import IsFaculty


class FacultyDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        faculty = request.user.faculty
        department = faculty.department

        # Total students
        total_students = Student.objects.filter(
            department=department,
            is_active=True
        ).count()

        # Average marks
        avg_marks = Marks.objects.filter(
            student__department=department
        ).aggregate(avg=Avg("marks_obtained"))["avg"]

        avg_marks = round(avg_marks, 2) if avg_marks else 0

        # Attendance %
        total_attendance = Attendance.objects.filter(
            student__department=department
        ).count()

        present_attendance = Attendance.objects.filter(
            student__department=department,
            status="P"
        ).count()

        attendance_percentage = (
            round((present_attendance / total_attendance) * 100, 2)
            if total_attendance > 0 else 0
        )

        # At risk students (marks < 40)
        at_risk_students = Marks.objects.filter(
            student__department=department,
            marks_obtained__lt=40
        ).values("student").distinct().count()

        return Response({
            "total_students": total_students,
            "attendance_percentage": attendance_percentage,
            "average_marks": avg_marks,
            "at_risk_students": at_risk_students
        })
# views.py

from django.db.models.functions import TruncMonth
from django.db.models import Avg
from collections import defaultdict


class FacultyPerformanceTrendAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        department = request.user.faculty.department

        data = (
            Marks.objects.filter(student__department=department)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(avg_marks=Avg("marks_obtained"))
            .order_by("month")
        )

        return Response(data)

from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Marks
from .permissions import IsFaculty


class FacultySubjectBreakdownAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        department = request.user.faculty.department

        data = (
            Marks.objects.filter(student__department=department)
            .values("subject__name")
            .annotate(avg_marks=Avg("marks_obtained"))
            .order_by("subject__name")
        )

        formatted = [
            {
                "subject": item["subject__name"],
                "avg_marks": round(item["avg_marks"], 2)
            }
            for item in data
        ]

        return Response(formatted)

from django.db.models import Avg, Count, Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Student, Marks, Attendance
from .permissions import IsFaculty


class FacultyRecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFaculty]

    def get(self, request):
        department = request.user.faculty.department

        students = Student.objects.filter(department=department)

        results = []

        for student in students:
            avg_marks = (
                Marks.objects.filter(student=student)
                .aggregate(avg=Avg("marks_obtained"))["avg"] or 0
            )

            total_days = Attendance.objects.filter(student=student).count()
            present_days = Attendance.objects.filter(
                student=student, status="P"
            ).count()

            attendance_percentage = (
                (present_days / total_days) * 100 if total_days > 0 else 0
            )

            risk_level = "Low"

            if avg_marks < 40 or attendance_percentage < 60:
                risk_level = "High"
            elif avg_marks < 50 or attendance_percentage < 70:
                risk_level = "Medium"

            results.append({
                "student": student.name,
                "roll_number": student.roll_number,
                "avg_marks": round(avg_marks, 2),
                "attendance": round(attendance_percentage, 2),
                "risk": risk_level
            })

        return Response(results)

import pandas as pd
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Profile


class BulkStudentRegisterView(APIView):

    @transaction.atomic
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        df = pd.read_excel(file)

        created_count = 0
        skipped_count = 0

        # 125 students per year
        year_distribution = [1]*125 + [2]*125 + [3]*125 + [4]*125

        for index, (_, row) in enumerate(df.iterrows()):
            roll = str(row["roll_number"]).strip()

            if User.objects.filter(username=roll).exists():
                skipped_count += 1
                continue

            assigned_year = year_distribution[index]

            # Create User
            user = User.objects.create_user(
                username=roll,
                password=roll
            )

            # Create Profile
            Profile.objects.create(
                user=user,
                role="STUDENT"
            )

            # Create Student
            Student.objects.create(
                user=user,
                name=roll,
                roll_number=roll,
                department="CSE",
                year=assigned_year
            )

            created_count += 1

        return Response(
            {
                "created": created_count,
                "skipped_existing": skipped_count
            },
            status=status.HTTP_201_CREATED
        )
 
    
from django.db.models import Count, Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ai_student_track.models import Attendance
from .permissions import IsStudent


class StudentAttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        student = request.user.student

        # ===============================
        # GET FILTERS
        # ===============================
        semester = request.GET.get("semester")
        subject_id = request.GET.get("subject_id")   # ✅ FIXED

        # Validate semester
        try:
            semester = int(semester) if semester else None
        except ValueError:
            return Response({"error": "Invalid semester"}, status=400)

        print("SEM:", semester, "SUBJECT_ID:", subject_id)

        # ===============================
        # BASE QUERY
        # ===============================
        attendance_qs = Attendance.objects.filter(student=student)

        # ===============================
        # APPLY FILTERS
        # ===============================

        # 🔥 Semester filter
        if semester:
            attendance_qs = attendance_qs.filter(
                subject__semester=semester
            )

        # 🔥 Year restriction
        attendance_qs = attendance_qs.filter(
            subject__year__lte=student.year
        )

        # 🔥 Subject filter (ID-based)
        if subject_id:
            try:
                subject_id = int(subject_id)
                attendance_qs = attendance_qs.filter(subject_id=subject_id)
            except ValueError:
                return Response({"error": "Invalid subject_id"}, status=400)

        # ===============================
        # CALCULATIONS
        # ===============================
        total_classes = attendance_qs.count()
        total_present = attendance_qs.filter(status="P").count()

        overall_percentage = (
            (total_present / total_classes) * 100
            if total_classes > 0 else 0
        )

        # ===============================
        # RESPONSE
        # ===============================
        return Response({
            "total_classes": total_classes,
            "total_present": total_present,   # ✅ added (useful)
            "overall_percentage": round(overall_percentage, 2)
        })
    
class StudentAttendanceHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        student = request.user.student

        # ===============================
        # GET FILTERS
        # ===============================
        semester = request.GET.get("semester")
        subject_id = request.GET.get("subject_id")   # ✅ FIXED (ID instead of name)
        status = request.GET.get("status")

        # Validate semester
        try:
            semester = int(semester) if semester else None
        except ValueError:
            return Response({"error": "Invalid semester"}, status=400)

        print("SEM:", semester, "SUBJECT_ID:", subject_id, "STATUS:", status)

        # ===============================
        # BASE QUERY
        # ===============================
        attendance_qs = Attendance.objects.filter(student=student)

        # ===============================
        # APPLY FILTERS SAFELY
        # ===============================

        # 🔥 Semester filter
        if semester:
            attendance_qs = attendance_qs.filter(
                subject__semester=semester
            )

        # 🔥 Year restriction (important logic)
        attendance_qs = attendance_qs.filter(
            subject__year__lte=student.year
        )

        # 🔥 Subject filter (ID based — robust)
        if subject_id:
            try:
                subject_id = int(subject_id)
                attendance_qs = attendance_qs.filter(subject_id=subject_id)
            except ValueError:
                return Response({"error": "Invalid subject_id"}, status=400)

        # 🔥 Status filter (normalized)
        if status:
            status = status.upper()
            if status not in ["P", "A"]:
                return Response({"error": "Invalid status"}, status=400)
            attendance_qs = attendance_qs.filter(status=status)

        # ===============================
        # OPTIMIZATION
        # ===============================
        attendance_qs = attendance_qs.select_related("subject").order_by("-date")

        # ===============================
        # RESPONSE
        # ===============================
        data = [
            {
                "subject": att.subject.name,
                "subject_id": att.subject.id,   # ✅ useful for frontend
                "date": att.date,
                "status": att.status
            }
            for att in attendance_qs
        ]

        return Response(data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ml.recommendation_predict import get_recommendation
from ml.trend_predict import predict_trend

from .models import Attendance, Marks, Student


class RecommendationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # ===============================
        # GET STUDENT
        # ===============================

        student = Student.objects.get(user=request.user)

        # ===============================
        # ATTENDANCE CALCULATION
        # ===============================

        attendance_records = Attendance.objects.filter(student=student)

        total = attendance_records.count()

        present = attendance_records.filter(
            status__in=["PRESENT", "Present", "present", "P"]
        ).count()

        attendance_percentage = (present / total) * 100 if total else 0

        # ===============================
        # MARKS CALCULATION
        # ===============================

        marks = Marks.objects.filter(student=student)

        mid_marks = marks.filter(
            exam_type="MID"
        ).values_list("marks_obtained", flat=True)

        internal_marks = marks.filter(
            exam_type="INT"
        ).values_list("marks_obtained", flat=True)

        final_marks = marks.filter(
            exam_type="FIN"
        ).values_list("marks_obtained", flat=True)

        mid_avg = sum(mid_marks) / len(mid_marks) if mid_marks else 0
        internal_avg = sum(internal_marks) / len(internal_marks) if internal_marks else 0
        final_avg = sum(final_marks) / len(final_marks) if final_marks else 0

        average_marks = (mid_avg + internal_avg + final_avg) / 3

        # ===============================
        # ML RECOMMENDATION
        # ===============================

        recommendation = get_recommendation(
            attendance_percentage,
            mid_avg,
            internal_avg,
            final_avg,
            average_marks
        )

        # ===============================
        # PERFORMANCE LEVEL
        # ===============================

        if average_marks >= 75:
            performance = "High"
        elif average_marks >= 50:
            performance = "Medium"
        else:
            performance = "Low"

        # ===============================
        # RISK LEVEL
        # ===============================

        if attendance_percentage < 60 or average_marks < 50:
            risk = "High"
        elif attendance_percentage < 75:
            risk = "Medium"
        else:
            risk = "Low"

        # ===============================
        # SUBJECT RISK PREDICTION
        # ===============================

        subject_risk = []

        subjects = marks.values("subject__name").distinct()

        for s in subjects:

            subject_name = s["subject__name"]

            subject_marks = marks.filter(
                subject__name=subject_name
            ).values_list("marks_obtained", flat=True)

            avg = sum(subject_marks) / len(subject_marks)

            if avg < 40:
                risk_level = "High Risk"
            elif avg < 60:
                risk_level = "Medium Risk"
            else:
                risk_level = "Low Risk"

            subject_risk.append({
                "subject": subject_name,
                "risk": risk_level
            })

        # ===============================
        # EXAM TREND ANALYSIS (ML MODEL)
        # ===============================

        trend_analysis = []

        subjects = marks.values("subject__name").distinct()

        for s in subjects:

            subject_name = s["subject__name"]

            mid = marks.filter(
                subject__name=subject_name,
                exam_type="MID"
            ).values_list("marks_obtained", flat=True)

            internal = marks.filter(
                subject__name=subject_name,
                exam_type="INT"
            ).values_list("marks_obtained", flat=True)

            final = marks.filter(
                subject__name=subject_name,
                exam_type="FIN"
            ).values_list("marks_obtained", flat=True)

            mid_mark = sum(mid) / len(mid) if mid else 0
            internal_mark = sum(internal) / len(internal) if internal else 0
            final_mark = sum(final) / len(final) if final else 0

            trend, message = predict_trend(
                mid_mark,
                internal_mark,
                final_mark
            )

            trend_analysis.append({
                "subject": subject_name,
                "mid": round(mid_mark, 2),
                "internal": round(internal_mark, 2),
                "final": round(final_mark, 2),
                "trend": trend,
                "message": message
            })

        # ===============================
        # MULTIPLE RECOMMENDATIONS
        # ===============================

        recommendations = [
            recommendation,
            "Increase attendance above 75%",
            "Revise internal assessments weekly",
        ]

        # ===============================
        # RESPONSE
        # ===============================

        return Response({

            "attendance_percentage": round(attendance_percentage, 2),

            "average_marks": round(average_marks, 2),

            "performance_level": performance,

            "risk_level": risk,

            "recommendations": recommendations,

            "subject_risk": subject_risk,

            "trend_analysis": trend_analysis

        })

class StudentSubjectListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        student = request.user.student
        semester = request.GET.get("semester")

        subjects = Subject.objects.filter(
            department=student.department,
            year__lte=student.year,  
            semester=semester
        )

        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ml.recommendation_predict import get_recommendation
from ml.trend_predict import predict_trend

from .models import Attendance, Marks, Student


class RecommendationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # ===============================
        # GET STUDENT
        # ===============================

        student = Student.objects.get(user=request.user)

        # ===============================
        # ATTENDANCE CALCULATION
        # ===============================

        attendance_records = Attendance.objects.filter(student=student)

        total = attendance_records.count()

        present = attendance_records.filter(
            status__in=["PRESENT", "Present", "present", "P"]
        ).count()

        attendance_percentage = (present / total) * 100 if total else 0

        # ===============================
        # MARKS CALCULATION
        # ===============================

        marks = Marks.objects.filter(student=student)

        mid_marks = marks.filter(
            exam_type="MID"
        ).values_list("marks_obtained", flat=True)

        internal_marks = marks.filter(
            exam_type="INT"
        ).values_list("marks_obtained", flat=True)

        final_marks = marks.filter(
            exam_type="FIN"
        ).values_list("marks_obtained", flat=True)

        mid_avg = sum(mid_marks) / len(mid_marks) if mid_marks else 0
        internal_avg = sum(internal_marks) / len(internal_marks) if internal_marks else 0
        final_avg = sum(final_marks) / len(final_marks) if final_marks else 0

        average_marks = (mid_avg + internal_avg + final_avg) / 3

        # ===============================
        # ML RECOMMENDATION
        # ===============================

        recommendation = get_recommendation(
            attendance_percentage,
            mid_avg,
            internal_avg,
            final_avg,
            average_marks
        )

        # ===============================
        # PERFORMANCE LEVEL
        # ===============================

        if average_marks >= 75:
            performance = "High"
        elif average_marks >= 50:
            performance = "Medium"
        else:
            performance = "Low"

        # ===============================
        # RISK LEVEL
        # ===============================

        if attendance_percentage < 60 or average_marks < 50:
            risk = "High"
        elif attendance_percentage < 75:
            risk = "Medium"
        else:
            risk = "Low"

        # ===============================
        # SUBJECT RISK PREDICTION
        # ===============================

        subject_risk = []

        subjects = marks.values("subject__name").distinct()

        for s in subjects:

            subject_name = s["subject__name"]

            subject_marks = marks.filter(
                subject__name=subject_name
            ).values_list("marks_obtained", flat=True)

            avg = sum(subject_marks) / len(subject_marks)

            if avg < 40:
                risk_level = "High Risk"
            elif avg < 60:
                risk_level = "Medium Risk"
            else:
                risk_level = "Low Risk"

            subject_risk.append({
                "subject": subject_name,
                "risk": risk_level
            })

        # ===============================
        # EXAM TREND ANALYSIS (ML MODEL)
        # ===============================

        trend_analysis = []

        subjects = marks.values("subject__name").distinct()

        for s in subjects:

            subject_name = s["subject__name"]

            mid = marks.filter(
                subject__name=subject_name,
                exam_type="MID"
            ).values_list("marks_obtained", flat=True)

            internal = marks.filter(
                subject__name=subject_name,
                exam_type="INT"
            ).values_list("marks_obtained", flat=True)

            final = marks.filter(
                subject__name=subject_name,
                exam_type="FIN"
            ).values_list("marks_obtained", flat=True)

            mid_mark = sum(mid) / len(mid) if mid else 0
            internal_mark = sum(internal) / len(internal) if internal else 0
            final_mark = sum(final) / len(final) if final else 0

            trend, message = predict_trend(
                mid_mark,
                internal_mark,
                final_mark
            )

            trend_analysis.append({
                "subject": subject_name,
                "mid": round(mid_mark, 2),
                "internal": round(internal_mark, 2),
                "final": round(final_mark, 2),
                "trend": trend,
                "message": message
            })

        # ===============================
        # MULTIPLE RECOMMENDATIONS
        # ===============================

        recommendations = [
            recommendation,
            "Increase attendance above 75%",
            "Revise internal assessments weekly",
        ]

        # ===============================
        # RESPONSE
        # ===============================

        return Response({

            "attendance_percentage": round(attendance_percentage, 2),

            "average_marks": round(average_marks, 2),

            "performance_level": performance,

            "risk_level": risk,

            "recommendations": recommendations,

            "subject_risk": subject_risk,

            "trend_analysis": trend_analysis

        })


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Avg

from .models import Attendance, Marks
from ml.insights import generate_ai_insight
from ml.recommendation import generate_recommendation


class SubjectRiskPredictionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        student = request.user.student

        # ===============================
        # GET SEMESTER
        # ===============================
        semester = request.GET.get("semester")

        try:
            semester = int(semester) if semester else None
        except ValueError:
            return Response({"error": "Invalid semester"}, status=400)

        print("SEM:", semester)

        # ===============================
        # GET SUBJECTS (CONTROLLED SOURCE)
        # ===============================
        subjects = Subject.objects.filter(
            department=student.department,
            year__lte=student.year
        )

        if semester:
            subjects = subjects.filter(semester=semester)

        # ===============================
        # BASE DATA
        # ===============================
        attendance_records = Attendance.objects.filter(student=student)
        marks_records = Marks.objects.filter(student=student)

        results = []

        # ===============================
        # LOOP SUBJECTS
        # ===============================
        for subject in subjects:

            # -----------------------------
            # Attendance
            # -----------------------------
            subject_attendance = attendance_records.filter(subject=subject)

            total_classes = subject_attendance.count()

            present_classes = subject_attendance.filter(
                status__in=["P", "Present", "present", "PRESENT"]
            ).count()

            attendance_percentage = (
                (present_classes / total_classes) * 100
                if total_classes > 0 else 0
            )

            # -----------------------------
            # Marks
            # -----------------------------
            subject_marks = marks_records.filter(subject=subject)

            avg_marks = subject_marks.aggregate(
                avg=Avg("marks_obtained")
            )["avg"] or 0

            # ===============================
            # 🔥 FIX 1: SKIP ONLY IF NO DATA AT ALL
            # ===============================
            if total_classes == 0 and avg_marks == 0:
                continue

            # -----------------------------
            # Risk Logic
            # -----------------------------
            if attendance_percentage < 60 or avg_marks < 40:
                risk = "High Risk"
            elif attendance_percentage < 75 or avg_marks < 55:
                risk = "Medium Risk"
            else:
                risk = "Low Risk"

            # -----------------------------
            # AI Insight
            # -----------------------------
            ai_insight = generate_ai_insight(
                subject.name,
                attendance_percentage,
                avg_marks
            )

            # -----------------------------
            # Recommendation
            # -----------------------------
            recommendation = generate_recommendation(
                subject.name,
                attendance_percentage,
                avg_marks,
                risk
            )

            # -----------------------------
            # Append Result
            # -----------------------------
            results.append({
                "subject": subject.name,
                "attendance": round(attendance_percentage, 2),
                "average_marks": round(avg_marks, 2),
                "risk": risk,
                "ai_insight": ai_insight,
                "recommendation": recommendation
            })

        # ===============================
        # 🔥 FIX 2: EMPTY RESPONSE HANDLING
        # ===============================
        return Response(results)