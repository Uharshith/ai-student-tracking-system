from django.db import models
from django.contrib.auth.models import User


# =========================
# COLLEGE
# =========================

class College(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


# =========================
# PROFILE
# =========================

class Profile(models.Model):

    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# =========================
# STUDENT
# =========================

class Student(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student")

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="students"
    )

    name = models.CharField(max_length=100)

    roll_number = models.CharField(max_length=20, unique=True, db_index=True)

    department = models.CharField(max_length=50, db_index=True)

    year = models.IntegerField(db_index=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.roll_number} - {self.name}"


# =========================
# FACULTY
# =========================

class Faculty(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty")

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="faculties"
    )

    name = models.CharField(max_length=100)

    department = models.CharField(max_length=50, db_index=True)

    designation = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# =========================
# SUBJECT
# =========================

class Subject(models.Model):

    name = models.CharField(max_length=100)

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    department = models.CharField(max_length=50, db_index=True)

    year = models.IntegerField(db_index=True)

    semester = models.IntegerField(db_index=True)

    def __str__(self):
        return f"{self.name} (Sem {self.semester})"


# =========================
# ATTENDANCE
# =========================

class Attendance(models.Model):

    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    date = models.DateField(db_index=True)

    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    entered_by = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="entered_attendance"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'date')
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['subject', 'date']),
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.name} - {self.date}"


# =========================
# MARKS
# =========================

class Marks(models.Model):

    EXAM_TYPE_CHOICES = (
        ('MID', 'Midterm'),
        ('INT', 'Internal'),
        ('FIN', 'Final'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="marks"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="marks"
    )

    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)

    marks_obtained = models.FloatField()

    entered_by = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="entered_marks"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'exam_type')
        indexes = [
            models.Index(fields=['student', 'exam_type']),
            models.Index(fields=['subject', 'exam_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.name} - {self.exam_type}"