import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from ai_student_track.models import Student, Subject, Attendance
from django.contrib.auth.models import User


# =========================
# CONFIG (ONLY CHANGE THIS)
# =========================
FILE_PATH = "sem7_attendance_generated.xlsx"
YEAR = 4
SEMESTER = 7


# =========================
# NORMALIZER
# =========================
def normalize(text):
    return str(text).strip().lower()


print("🚀 Starting attendance import...")


# =========================
# LOAD FILE
# =========================
df = pd.read_excel(FILE_PATH)

print("📊 Original Columns:", list(df.columns))

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

print("📊 Cleaned Columns:", list(df.columns))


# =========================
# FIX COLUMN NAMES
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
# CHECK DUPLICATES IN FILE
# =========================
duplicates = df.duplicated(subset=["roll_number", "subject", "date"])

if duplicates.any():
    print(f"⚠️ Found {duplicates.sum()} duplicate rows in file")


# =========================
# GET FACULTY
# =========================
faculty_user = User.objects.filter(username="faculty1").first()

if not faculty_user or not hasattr(faculty_user, "faculty"):
    raise Exception("❌ Faculty 'faculty1' not found or not linked")

faculty = faculty_user.faculty


# =========================
# PRELOAD STUDENTS
# =========================
students = {
    normalize(s.roll_number): s
    for s in Student.objects.all()
}


# =========================
# PRELOAD SUBJECTS (🔥 DYNAMIC)
# =========================
subjects_qs = Subject.objects.filter(year=YEAR, semester=SEMESTER)

if not subjects_qs.exists():
    raise Exception(f"❌ No subjects found for Year {YEAR}, Semester {SEMESTER}")

subjects = {
    normalize(s.name): s
    for s in subjects_qs
}

print("\n📚 Subjects loaded from DB:")
for s in subjects_qs:
    print("-", s.name)


# =========================
# EXISTING DATA
# =========================
existing = set(
    Attendance.objects.filter(subject__semester=SEMESTER)
    .values_list("student_id", "subject_id", "date")
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

        # -------------------------
        # DATE
        # -------------------------
        date_value = pd.to_datetime(row["date"], errors="coerce", dayfirst=True)

        if pd.isna(date_value):
            print(f"❌ Invalid date at row {i}")
            skipped += 1
            continue

        date_value = date_value.date()

        # -------------------------
        # STUDENT
        # -------------------------
        student = students.get(roll)

        if not student:
            print(f"❌ Student not found: {roll}")
            skipped += 1
            continue

        # -------------------------
        # SUBJECT (🔥 NO HARDCODING)
        # -------------------------
        subject = subjects.get(subject_name)

        if not subject:
            print(f"❌ Subject not found in DB: {subject_name}")
            skipped += 1
            continue

        # -------------------------
        # DUPLICATE
        # -------------------------
        key = (student.id, subject.id, date_value)

        if key in existing:
            skipped += 1
            continue

        # -------------------------
        # STATUS
        # -------------------------
        if status_value in ["present", "p"]:
            status_code = "P"
        elif status_value in ["absent", "a"]:
            status_code = "A"
        else:
            print(f"❌ Invalid status at row {i}: {status_value}")
            skipped += 1
            continue

        # -------------------------
        # CREATE
        # -------------------------
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

        # -------------------------
        # BULK INSERT
        # -------------------------
        if len(attendance_objects) >= batch_size:
            Attendance.objects.bulk_create(attendance_objects)
            attendance_objects = []
            print(f"⚡ Inserted {inserted} records...")

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
print("\n==========================")
print("✅ Attendance inserted:", inserted)
print("⚠️ Rows skipped:", skipped)
print("🎯 Import completed")
print("==========================")