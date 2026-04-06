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
FILE_PATH = "sem7_marks_generated.xlsx"   # change file
YEAR = 4
SEMESTER = 7


# =========================
# NORMALIZER
# =========================
def normalize(text):
    return str(text).strip().lower()


print("🚀 Starting marks import...")


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
if "roll_number" not in df.columns:
    if "register_number" in df.columns:
        df.rename(columns={"register_number": "roll_number"}, inplace=True)
    elif "register_no" in df.columns:
        df.rename(columns={"register_no": "roll_number"}, inplace=True)
    else:
        raise Exception(f"❌ No roll number column found: {df.columns}")

df.rename(columns={"marks": "marks_obtained"}, inplace=True)


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
    raise Exception("❌ Faculty not found")

faculty = faculty_user.faculty


# =========================
# PRELOAD STUDENTS
# =========================
students = {
    normalize(s.roll_number): s
    for s in Student.objects.all()
}


# =========================
# PRELOAD SUBJECTS (DYNAMIC)
# =========================
subjects_qs = Subject.objects.filter(year=YEAR, semester=SEMESTER)

if not subjects_qs.exists():
    raise Exception(f"❌ No subjects found for Year {YEAR}, Sem {SEMESTER}")

subjects = {
    normalize(s.name): s
    for s in subjects_qs
}

print("\n📚 Subjects in DB:")
for s in subjects_qs:
    print("-", s.name)


# =========================
# EXISTING DATA
# =========================
existing = set(
    Marks.objects.filter(subject__semester=SEMESTER)
    .values_list("student_id", "subject_id", "exam_type")
)


# =========================
# VALID EXAMS
# =========================
VALID_EXAMS = ["INT", "MID", "FIN"]


# =========================
# DEDUP EXCEL
# =========================
dedup_map = {}

for i, row in df.iterrows():
    roll = normalize(row["roll_number"])
    subject_name = normalize(row["subject"])
    exam_type = str(row["exam_type"]).strip().upper()

    key = (roll, subject_name, exam_type)
    dedup_map[key] = row   # last occurrence wins

print(f"📦 Unique records after dedup: {len(dedup_map)}")


# =========================
# PROCESS
# =========================
marks_objects = []
inserted = 0
skipped = 0
invalid_subjects = set()
batch_size = 5000


for key, row in dedup_map.items():
    try:
        roll, subject_name, exam_type = key

        if exam_type not in VALID_EXAMS:
            skipped += 1
            continue

        # MARKS VALIDATION
        try:
            marks_value = float(row["marks_obtained"])
        except:
            skipped += 1
            continue

        if not (0 <= marks_value <= 100):
            print(f"❌ Invalid marks: {marks_value}")
            skipped += 1
            continue

        student = students.get(roll)
        subject = subjects.get(subject_name)

        if not student:
            print(f"❌ Student not found: {roll}")
            skipped += 1
            continue

        if not subject:
            invalid_subjects.add(subject_name)
            skipped += 1
            continue

        db_key = (student.id, subject.id, exam_type)

        if db_key in existing:
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

        existing.add(db_key)
        inserted += 1

        if len(marks_objects) >= batch_size:
            Marks.objects.bulk_create(marks_objects)
            marks_objects = []
            print(f"⚡ Inserted {inserted} records...")

    except Exception as e:
        print(f"⚠️ Error: {e}")
        skipped += 1


# =========================
# FINAL INSERT
# =========================
if marks_objects:
    Marks.objects.bulk_create(marks_objects)


# =========================
# RESULT
# =========================
print("\n==========================")
print("✅ Marks inserted:", inserted)
print("⚠️ Rows skipped:", skipped)

if invalid_subjects:
    print("\n❌ Unknown subjects found:")
    for s in invalid_subjects:
        print("-", s)

print("🎯 Import completed")
print("==========================")