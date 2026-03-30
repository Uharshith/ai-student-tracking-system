def generate_ai_insight(subject, attendance, marks):

    issues = []
    strengths = []

    if attendance < 60:
        issues.append("low class attendance")

    if marks < 45:
        issues.append("weak exam performance")

    if attendance > 80:
        strengths.append("strong lecture participation")

    if marks > 70:
        strengths.append("good academic performance")

    if issues:
        issue_text = " and ".join(issues)
        insight = f"{subject} performance indicates {issue_text}. Focused effort is required to improve outcomes."

    else:
        strength_text = " and ".join(strengths)
        insight = f"{subject} shows {strength_text}. Maintain your current academic approach."

    return insight