import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth.models import User
from ai_student_track.models import Student, Profile, College

df = pd.read_excel("csbs_60_students_updated.xlsx")

users = []
profiles = []
students = []

for _, row in df.iterrows():

    username = str(row["username"])
    password = str(row["password"])
    name = row["name"]
    roll = row["roll_number"]
    dept = row["department"]
    year = int(row["year"])
    college_code = row["college_code"]

    college, _ = College.objects.get_or_create(
        code=college_code,
        defaults={"name": college_code}
    )

    user = User(
        username=username,
        first_name=name
    )

    user.set_password(password)
    users.append(user)

User.objects.bulk_create(users)

# reload users from DB
created_users = User.objects.filter(username__in=df["username"].tolist())

for user, (_, row) in zip(created_users, df.iterrows()):

    profiles.append(
        Profile(
            user=user,
            role="STUDENT"
        )
    )

    students.append(
        Student(
            user=user,
            name=row["name"],
            roll_number=row["roll_number"],
            department=row["department"],
            year=row["year"],
            college=College.objects.get(code=row["college_code"])
        )
    )

Profile.objects.bulk_create(profiles)
Student.objects.bulk_create(students)

print("Students inserted successfully")