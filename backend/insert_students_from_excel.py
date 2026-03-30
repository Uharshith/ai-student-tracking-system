import os
import django
import pandas as pd

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth.models import User
from ai_student_track.models import Student, Profile, College

# Load Excel file
file_path = "csbs_60_students_updated.xlsx"
df = pd.read_excel(file_path)

for _, row in df.iterrows():

    username = str(row["username"])
    password = str(row["password"])
    name = row["name"]
    roll_number = row["roll_number"]
    department = row["department"]
    year = int(row["year"])
    college_code = row["college_code"]

    # Get or create college
    college, _ = College.objects.get_or_create(
        code=college_code,
        defaults={"name": college_code}
    )

    # Create User
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=name
    )

    # Create Profile
    Profile.objects.create(
        user=user,
        role="STUDENT"
    )

    # Create Student
    Student.objects.create(
        user=user,
        name=name,
        roll_number=roll_number,
        department=department,
        year=year,
        college=college
    )

print("Students imported successfully")