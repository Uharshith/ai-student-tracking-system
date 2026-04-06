import random


def generate_recommendation(subject, attendance, marks, risk):

    pool = set()   # ensures uniqueness

    # ================= ATTENDANCE =================
    if attendance < 40:
        pool.update([
            f"Attendance in {subject} is critically low. Attend all classes.",
            f"You are missing too many {subject} lectures.",
            f"Revise missed topics immediately.",
            f"Create a strict attendance plan for {subject}.",
            f"Discuss missed lectures with peers."
        ])

    elif attendance < 70:
        pool.update([
            f"Attendance in {subject} needs improvement.",
            f"Be more consistent in attending {subject} classes.",
            f"Avoid skipping important lectures.",
            f"Participate actively during classes.",
            f"Review class notes weekly."
        ])

    else:
        pool.update([
            f"Excellent attendance in {subject}.",
            f"You maintain strong discipline in attending classes.",
            f"Keep participating actively.",
            f"Use classroom time effectively.",
            f"Continue this consistency."
        ])

    # ================= MARKS =================
    if marks < 40:
        pool.update([
            f"Your performance in {subject} is weak.",
            f"Focus on fundamental concepts.",
            f"Practice basic problems daily.",
            f"Revise core topics repeatedly.",
            f"Seek help from faculty."
        ])

    elif marks < 70:
        pool.update([
            f"Your performance in {subject} is average.",
            f"Increase problem-solving practice.",
            f"Focus on application-based questions.",
            f"Revise important concepts regularly.",
            f"Solve previous year papers."
        ])

    else:
        pool.update([
            f"You are performing well in {subject}.",
            f"Try solving advanced problems.",
            f"Focus on mastering difficult topics.",
            f"Push your performance further.",
            f"Maintain your study strategy."
        ])

    # ================= RISK =================
    if risk == "High Risk":
        pool.update([
            f"{subject} requires urgent attention.",
            f"Allocate more study time daily.",
            f"Create a strict study schedule.",
            f"Prioritize this subject over others.",
            f"Track your progress regularly."
        ])

    elif risk == "Medium Risk":
        pool.update([
            f"{subject} shows moderate risk.",
            f"Improve consistency in preparation.",
            f"Monitor progress weekly.",
            f"Practice regularly to improve stability.",
            f"Focus on weak areas."
        ])

    else:
        pool.update([
            f"{subject} performance is stable.",
            f"Maintain your current strategy.",
            f"Continue regular revision.",
            f"Keep practicing consistently.",
            f"No immediate risk detected."
        ])

    # ================= 🔥 RESOURCES =================
    pool.update([
        f"Watch YouTube tutorials for {subject} concepts.",
        f"Refer to standard textbooks for deeper understanding.",
        f"Use GeeksforGeeks for practice in {subject}.",
        f"Practice problems on LeetCode related to {subject}.",
        f"Take online quizzes to test your knowledge.",
        f"Join peer study groups for {subject}.",
        f"Use flashcards for quick revision.",
        f"Solve mock tests regularly.",
        f"Use online platforms like Coursera for {subject}.",
        f"Revise notes before exams consistently."
    ])

    # ================= FINAL =================
    pool = list(pool)
    random.shuffle(pool)

    return pool[:8]   # 🔥 ALWAYS 8 UNIQUE