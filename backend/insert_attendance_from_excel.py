import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from ai_student_track.models import Student, Subject, Attendance
from django.contrib.auth.models import User


# =========================
# CONFIG
# =========================
FILE_PATH = "sem2_attendance.xlsx"
YEAR = 1
SEMESTER = 2


# =========================
# HELPER
# =========================
def normalize(text):
    return str(text).strip().lower()


print("🚀 Starting attendance import...")


# =========================
# LOAD FILE
# =========================
df = pd.read_excel(FILE_PATH)

# 🔥 ALWAYS PRINT COLUMNS (DEBUG)
print("📊 Columns in file:", list(df.columns))

# Normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")


# =========================
# FIX COLUMN NAMES (ROBUST)
# =========================
if "register_number" in df.columns:
    df.rename(columns={"register_number": "roll_number"}, inplace=True)
elif "register_no" in df.columns:
    df.rename(columns={"register_no": "roll_number"}, inplace=True)
elif "roll_number" in df.columns:
    pass
else:
    raise Exception(f"❌ No roll number column found. Found: {df.columns}")


# =========================
# VALIDATE COLUMNS
# =========================
required_columns = ["roll_number", "subject", "date", "status"]

for col in required_columns:
    if col not in df.columns:
        raise Exception(f"❌ Missing column: {col}")


# =========================
# GET FACULTY
# =========================
faculty_user = User.objects.filter(username="faculty1").first()

if not faculty_user or not hasattr(faculty_user, "faculty"):
    raise Exception("❌ Faculty 'faculty1' not found or not linked")

faculty = faculty_user.faculty


# =========================
# PRELOAD DATA
# =========================
students = {
    normalize(s.roll_number): s
    for s in Student.objects.all()
}

subjects = {
    normalize(s.name): s
    for s in Subject.objects.filter(year=YEAR, semester=SEMESTER)
}


# =========================
# EXISTING DATA
# =========================
existing = set(
    Attendance.objects.values_list("student_id", "subject_id", "date")
)


# =========================
# PROCESS DATA
# =========================
attendance_objects = []
inserted = 0
skipped = 0
batch_size = 5000


for i, row in df.iterrows():
    try:
        roll = normalize(row["roll_number"])
        subject_name = normalize(row["subject"])
        status_value = normalize(row["status"])

        # DATE PARSE
        date_value = pd.to_datetime(row["date"], errors="coerce", dayfirst=True)

        if pd.isna(date_value):
            print(f"❌ Invalid date at row {i}")
            skipped += 1
            continue

        date_value = date_value.date()

        # STUDENT CHECK
        student = students.get(roll)
        if not student:
            print(f"❌ Student not found: {roll}")
            skipped += 1
            continue

        # SUBJECT CHECK (SEM FIXED)
        subject = subjects.get(subject_name)
        if not subject:
            print(f"❌ Subject not found (SEM {SEMESTER}): {subject_name}")
            skipped += 1
            continue

        # DUPLICATE CHECK
        key = (student.id, subject.id, date_value)
        if key in existing:
            skipped += 1
            continue

        # STATUS VALIDATION
        if status_value in ["present", "p"]:
            status_code = "P"
        elif status_value in ["absent", "a"]:
            status_code = "A"
        else:
            print(f"❌ Invalid status at row {i}: {status_value}")
            skipped += 1
            continue

        attendance_objects.append(
            Attendance(
                student=student,
                subject=subject,
                date=date_value,
                status=status_code,
                entered_by=faculty
            )
        )

        existing.add(key)
        inserted += 1

        # BULK INSERT
        if len(attendance_objects) >= batch_size:
            Attendance.objects.bulk_create(attendance_objects)
            attendance_objects = []

    except Exception as e:
        print(f"⚠️ Error at row {i}: {e}")
        skipped += 1


# =========================
# FINAL INSERT
# =========================
if attendance_objects:
    Attendance.objects.bulk_create(attendance_objects)


# =========================
# RESULT
# =========================
print("✅ Attendance inserted:", inserted)
print("⚠️ Rows skipped:", skipped)
print("🎯 Import completed successfully")