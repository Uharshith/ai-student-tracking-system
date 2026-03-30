import random


def generate_recommendation(subject, attendance, marks, risk):

    recommendations = []

    # ---------------- Attendance Analysis ----------------

    if attendance < 20:

        attendance_recommendations = [
            f"Attendance in {subject} is critically low. Immediate class participation is required.",
            f"You have missed most {subject} lectures. Start attending classes regularly.",
            f"Low attendance in {subject} may affect academic performance. Prioritize lectures.",
            f"Meet your faculty to understand missed topics in {subject}.",
            f"Plan a strict schedule to attend all upcoming {subject} classes."
        ]

    elif attendance < 40:

        attendance_recommendations = [
            f"Attendance in {subject} is significantly below academic expectations.",
            f"Try to improve classroom participation in {subject}.",
            f"Attend all remaining lectures of {subject} to avoid academic risk.",
            f"Review lecture materials regularly for {subject}.",
            f"Set reminders to attend every {subject} class."
        ]

    elif attendance < 60:

        attendance_recommendations = [
            f"Attendance in {subject} is moderate but can still be improved.",
            f"Regular participation in {subject} lectures will strengthen understanding.",
            f"Make sure not to miss important {subject} classes.",
            f"Review lecture notes weekly for {subject}.",
            f"Stay consistent with class attendance in {subject}."
        ]

    elif attendance < 80:

        attendance_recommendations = [
            f"Attendance in {subject} is good but still has room for improvement.",
            f"Maintaining consistent attendance will support better learning in {subject}.",
            f"Continue participating actively in {subject} classes.",
            f"Use classroom discussions to clarify doubts in {subject}.",
            f"Regular attendance will help reinforce key {subject} concepts."
        ]

    else:

        attendance_recommendations = [
            f"Excellent attendance record in {subject}.",
            f"You consistently attend {subject} lectures. Keep it up.",
            f"Strong classroom engagement in {subject} is evident.",
            f"Continue maintaining this attendance level in {subject}.",
            f"Your commitment to attending {subject} classes is commendable."
        ]

    recommendations.append(random.choice(attendance_recommendations))


    # ---------------- Marks Analysis ----------------

    if marks < 20:

        marks_recommendations = [
            f"Performance in {subject} is very low. Focus on fundamental concepts.",
            f"Start revising basic topics in {subject}.",
            f"Seek help from faculty for difficult concepts in {subject}.",
            f"Practice simple exercises regularly for {subject}.",
            f"Allocate more study time to {subject}."
        ]

    elif marks < 40:

        marks_recommendations = [
            f"Marks in {subject} indicate weak conceptual understanding.",
            f"Increase practice for {subject} problem-solving.",
            f"Review previous question papers for {subject}.",
            f"Focus on strengthening key concepts in {subject}.",
            f"Regular revision will help improve performance in {subject}."
        ]

    elif marks < 60:

        marks_recommendations = [
            f"Performance in {subject} is moderate.",
            f"More practice can significantly improve results in {subject}.",
            f"Solve additional exercises related to {subject}.",
            f"Focus on application-based problems in {subject}.",
            f"Consistent study will help strengthen {subject} understanding."
        ]

    elif marks < 80:

        marks_recommendations = [
            f"Marks in {subject} are good.",
            f"Continue practicing advanced problems in {subject}.",
            f"Regular revision will maintain strong performance in {subject}.",
            f"Focus on mastering complex topics in {subject}.",
            f"Try solving higher difficulty questions in {subject}."
        ]

    else:

        marks_recommendations = [
            f"Excellent academic performance in {subject}.",
            f"Your understanding of {subject} concepts is strong.",
            f"Maintain your current preparation strategy in {subject}.",
            f"Continue solving advanced problems in {subject}.",
            f"You demonstrate strong academic capability in {subject}."
        ]

    recommendations.append(random.choice(marks_recommendations))


    # ---------------- Risk Analysis ----------------

    if risk == "High Risk":

        risk_recommendations = [
            f"{subject} is currently categorized as a high academic risk.",
            f"Immediate improvement strategies should be applied for {subject}.",
            f"Prioritize structured study sessions for {subject}.",
            f"Develop a focused revision plan for {subject}.",
            f"Seek guidance from faculty for improving performance in {subject}."
        ]

    elif risk == "Medium Risk":

        risk_recommendations = [
            f"{subject} shows moderate academic risk.",
            f"Consistent practice can improve {subject} performance.",
            f"Regular revision sessions will help stabilize {subject} results.",
            f"Monitor progress in {subject} closely.",
            f"Increase practice frequency for {subject}."
        ]

    else:

        risk_recommendations = [
            f"{subject} performance is stable.",
            f"Current study approach for {subject} is effective.",
            f"Maintain regular revision for {subject}.",
            f"Continue practicing concepts in {subject}.",
            f"No immediate academic risk detected in {subject}."
        ]

    recommendations.append(random.choice(risk_recommendations))


    return recommendations