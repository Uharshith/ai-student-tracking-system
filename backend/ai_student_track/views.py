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
from django.db.models import Avg

from .models import Subject, Attendance, Marks
from ml.insights import generate_ai_insight
from ml.recommendation import generate_recommendation
from ml.trend_predict import predict_trend
from ml.recommendation_predict import get_recommendation


class SubjectRiskPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        student = request.user.student
        semester = request.GET.get("semester")

        try:
            semester = int(semester) if semester else None
        except ValueError:
            return Response({"error": "Invalid semester"}, status=400)

        subjects = Subject.objects.filter(
            department=student.department,
            year__lte=student.year
        )

        if semester:
            subjects = subjects.filter(semester=semester)

        results = []

        for subject in subjects:

            # ================= ATTENDANCE =================
            attendance_qs = Attendance.objects.filter(
                student=student,
                subject=subject
            )

            total = attendance_qs.count()
            present = attendance_qs.filter(status="P").count()

            attendance = (present / total * 100) if total else 0

            # ================= MARKS =================
            mid = Marks.objects.filter(
                student=student, subject=subject, exam_type="MID"
            ).aggregate(avg=Avg("marks_obtained"))["avg"] or 0

            internal = Marks.objects.filter(
                student=student, subject=subject, exam_type="INT"
            ).aggregate(avg=Avg("marks_obtained"))["avg"] or 0

            final = Marks.objects.filter(
                student=student, subject=subject, exam_type="FIN"
            ).aggregate(avg=Avg("marks_obtained"))["avg"] or 0

            avg_marks = (mid + internal + final) / 3 if (mid or internal or final) else 0

            # ================= SKIP EMPTY =================
            if attendance == 0 and avg_marks == 0:
                continue

            # ================= RISK =================
            if attendance < 60 or avg_marks < 40:
                risk = "High Risk"
            elif attendance < 75 or avg_marks < 60:
                risk = "Medium Risk"
            else:
                risk = "Low Risk"

            # ================= AI INSIGHT =================
            ai_insight = generate_ai_insight(
                subject.name,
                attendance,
                avg_marks
            )

            # ================= ML TREND =================
            trend, trend_message = predict_trend(mid, internal, final)

            # ================= ML RECOMMENDATION =================
            ml_recommendation = get_recommendation(
                attendance,
                mid,
                internal,
                final,
                avg_marks
            )

            # ================= RULE RECOMMENDATIONS =================
            rule_recommendations = generate_recommendation(
                subject.name,
                attendance,
                avg_marks,
                risk
            )

            # ================= FINAL (🔥 FIXED HERE) =================
            
            final_recommendations = [ml_recommendation] + rule_recommendations[:7]

            # ================= RESPONSE =================
            results.append({
                "subject": subject.name,
                "attendance": round(attendance, 2),
                "average_marks": round(avg_marks, 2),
                "risk": risk,
                "ai_insight": ai_insight,
                "recommendations": final_recommendations,
                "trend": trend,
                "trend_message": trend_message,
                "mid": round(mid, 2),
                "internal": round(internal, 2),
                "final": round(final, 2)
            })

        return Response(results)
    
       
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg

from .models import Subject, Attendance, Marks
from .permissions import IsStudent

# ✅ IMPORT YOUR NEW SMART RECOMMENDER
from ml.smart_recommendation import generate_smart_recommendation


class StudentDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):

        # ================= SAFE STUDENT FETCH =================
        try:
            student = request.user.student
        except:
            return Response({"error": "Student not found"}, status=400)

        # ================= CURRENT SEM =================
        current_sem = (
            Subject.objects.filter(
                department=student.department,
                year=student.year
            )
            .order_by("-semester")
            .values_list("semester", flat=True)
            .first()
        )

        if not current_sem:
            return Response({
                "attendance": 0,
                "average_marks": 0,
                "performance_level": "Low",
                "risk_level": "High",
                "recommendations": []
            })

        # ================= ATTENDANCE =================
        attendance_qs = Attendance.objects.filter(
            student=student,
            subject__semester=current_sem
        )

        total = attendance_qs.count()
        present = attendance_qs.filter(status="P").count()

        attendance = (present / total * 100) if total else 0

        # ================= MARKS =================
        marks_qs = Marks.objects.filter(
            student=student,
            subject__semester=current_sem,
            exam_type="FIN"
        ).exclude(subject__name__icontains="internship")

        avg_marks = marks_qs.aggregate(
            avg=Avg("marks_obtained")
        )["avg"] or 0

        # ================= BACKLOGS =================
        backlogs = marks_qs.filter(
            marks_obtained__lt=40
        ).count()

        # ================= PERFORMANCE LEVEL =================
        if avg_marks >= 75 and attendance >= 80:
            performance = "High"
        elif avg_marks >= 50 and attendance >= 65:
            performance = "Medium"
        else:
            performance = "Low"

        # ================= RISK LEVEL =================
        if avg_marks < 40 or attendance < 60:
            risk = "High"
        elif avg_marks < 55 or attendance < 70:
            risk = "Medium"
        else:
            risk = "Low"

        # ================= SMART RECOMMENDATIONS =================
        recommendations = generate_smart_recommendation(
            attendance,
            avg_marks,
            backlogs
        )

        # ================= FINAL RESPONSE =================
        return Response({
            "attendance": round(attendance, 2),
            "average_marks": round(avg_marks, 2),
            "performance_level": performance,
            "risk_level": risk,
            "recommendations": recommendations
        })
    

# views.py
from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Subject, Attendance, Marks


class SemesterPerformancePieAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            student = request.user.student
        except:
            return Response({"error": "Student not found"}, status=400)

        current_sem = (
            Subject.objects.filter(
                department=student.department,
                year=student.year
            )
            .order_by("-semester")
            .values_list("semester", flat=True)
            .first()
        )

        if not current_sem:
            return Response({"pie_data": []})

        subjects = Subject.objects.filter(
            department=student.department,
            year=student.year,
            semester=current_sem
        )

        high = 0
        medium = 0
        low = 0

        subject_breakdown = []

        for subject in subjects:

            attendance_qs = Attendance.objects.filter(
                student=student,
                subject=subject
            )

            total = attendance_qs.count()
            present = attendance_qs.filter(status="P").count()
            attendance = (present / total * 100) if total else 0

            mid = Marks.objects.filter(
                student=student, subject=subject, exam_type="MID"
            ).aggregate(avg=Avg("marks_obtained"))["avg"] or 0

            internal = Marks.objects.filter(
                student=student, subject=subject, exam_type="INT"
            ).aggregate(avg=Avg("marks_obtained"))["avg"] or 0

            final = Marks.objects.filter(
                student=student, subject=subject, exam_type="FIN"
            ).aggregate(avg=Avg("marks_obtained"))["avg"] or 0

            avg_marks = (mid + internal + final) / 3 if (mid or internal or final) else 0

            if attendance == 0 and avg_marks == 0:
                continue

            if attendance < 60 or avg_marks < 40:
                category = "High Risk"
                high += 1
            elif attendance < 75 or avg_marks < 60:
                category = "Medium Risk"
                medium += 1
            else:
                category = "Low Risk"
                low += 1

            subject_breakdown.append({
                "subject": subject.name,
                "attendance": round(attendance, 2),
                "average_marks": round(avg_marks, 2),
                "risk": category
            })

        pie_data = [
            {"name": "Low", "value": low},
            {"name": "Medium", "value": medium},
            {"name": "High", "value": high},
        ]

        return Response({
            "pie_data": pie_data,
            "subject_breakdown": subject_breakdown,
            "current_semester": current_sem
        })