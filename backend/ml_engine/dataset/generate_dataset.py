import pandas as pd
import random
import os

def generate_student_data(num_records=1000):
    data = []

    for _ in range(num_records):
        attendance = random.randint(40, 100)
        internal_marks = random.randint(30, 100)
        assignment_score = random.randint(30, 100)
        backlogs = random.randint(0, 3)

        # Logical labeling
        if attendance > 80 and internal_marks > 75 and assignment_score > 75 and backlogs == 0:
            performance = 2   # High
        elif attendance < 60 or backlogs >= 2:
            performance = 0   # Low
        else:
            performance = 1   # Medium

        data.append([
            attendance,
            internal_marks,
            assignment_score,
            backlogs,
            performance
        ])

    columns = [
        "attendance",
        "internal_marks",
        "assignment_score",
        "backlogs",
        "performance"
    ]

    df = pd.DataFrame(data, columns=columns)

    # Save inside same dataset folder
    file_path = os.path.join(os.path.dirname(__file__), "student_dataset.csv")
    df.to_csv(file_path, index=False)

    print("Dataset generated successfully!")

if __name__ == "__main__":
    generate_student_data()
