import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from ai_student_track.models import Student, Subject, Marks
from django.contrib.auth.models import User


# =========================
# CONFIG
# =========================
FILE_PATH = "sem2_marks_updated.xlsx"
YEAR = 1
SEMESTER = 2


# =========================
# HELPER
# =========================
def normalize(text):
    return str(text).strip().lower()


print("🚀 Starting marks import...")


# =========================
# LOAD FILE
# =========================
df = pd.read_excel(FILE_PATH)

# DEBUG
print("📊 Columns in file:", list(df.columns))

# Normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")


# =========================
# FIX COLUMN NAMES (ROBUST)
# =========================
if "roll_number" not in df.columns:
    if "register_number" in df.columns:
        df.rename(columns={"register_number": "roll_number"}, inplace=True)
    elif "register_no" in df.columns:
        df.rename(columns={"register_no": "roll_number"}, inplace=True)
    else:
        raise Exception(f"❌ No roll number column found: {df.columns}")

# Ensure standard names
rename_map = {
    "exam_type": "exam_type",
    "marks_obtained": "marks_obtained",
    "marks": "marks_obtained"
}
df.rename(columns=rename_map, inplace=True)


# =========================
# VALIDATE COLUMNS
# =========================
required_columns = ["roll_number", "subject", "exam_type", "marks_obtained"]

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
    Marks.objects.values_list("student_id", "subject_id", "exam_type")
)


# =========================
# VALID EXAM TYPES
# =========================
VALID_EXAMS = ["INT", "MID", "FIN"]


# =========================
# PROCESS DATA
# =========================
marks_objects = []
inserted = 0
skipped = 0
batch_size = 5000


for i, row in df.iterrows():
    try:
        roll = normalize(row["roll_number"])
        subject_name = normalize(row["subject"])
        exam_type = str(row["exam_type"]).strip().upper()

        # VALIDATE EXAM TYPE
        if exam_type not in VALID_EXAMS:
            print(f"❌ Invalid exam type at row {i}: {exam_type}")
            skipped += 1
            continue

        # MARKS VALIDATION
        try:
            marks_value = float(row["marks_obtained"])
        except:
            print(f"❌ Invalid marks at row {i}")
            skipped += 1
            continue

        student = students.get(roll)
        if not student:
            print(f"❌ Student not found: {roll}")
            skipped += 1
            continue

        subject = subjects.get(subject_name)
        if not subject:
            print(f"❌ Subject not found (SEM {SEMESTER}): {subject_name}")
            skipped += 1
            continue

        key = (student.id, subject.id, exam_type)

        if key in existing:
            skipped += 1
            continue

        marks_objects.append(
            Marks(
                student=student,
                subject=subject,
                exam_type=exam_type,
                marks_obtained=marks_value,
                entered_by=faculty
            )
        )

        existing.add(key)
        inserted += 1

        if len(marks_objects) >= batch_size:
            Marks.objects.bulk_create(marks_objects)
            marks_objects = []

    except Exception as e:
        print(f"⚠️ Error at row {i}: {e}")
        skipped += 1


# =========================
# FINAL INSERT
# =========================
if marks_objects:
    Marks.objects.bulk_create(marks_objects)


# =========================
# RESULT
# =========================
print("✅ Marks inserted:", inserted)
print("⚠️ Rows skipped:", skipped)
print("🎯 Marks import completed successfully")