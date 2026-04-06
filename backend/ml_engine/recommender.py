def generate_recommendation(prediction, attendance, avg_marks, backlogs):

    base = []

    # ===============================
    # ML BASE (your existing logic)
    # ===============================
    if prediction == 0:
        performance = "Low"
        risk = "High"
        base = [
            "Your academic performance is currently at risk.",
            "Immediate improvement is required to avoid failure."
        ]

    elif prediction == 1:
        performance = "Medium"
        risk = "Medium"
        base = [
            "Your performance is stable but needs improvement.",
            "You have potential to reach higher levels."
        ]

    elif prediction == 2:
        performance = "High"
        risk = "Low"
        base = [
            "You are performing well academically.",
            "Maintain consistency for continued success."
        ]

    else:
        return {
            "performance_level": "Unknown",
            "risk_level": "Unknown",
            "student_recommendations": []
        }

    # ===============================
    # DYNAMIC ADDITIONS (REAL POWER)
    # ===============================

    dynamic = []

    # Attendance logic
    if attendance < 60:
        dynamic += [
            "Your attendance is critically low. Attend all classes without fail.",
            "Missing classes is directly affecting your performance."
        ]
    elif attendance < 75:
        dynamic += [
            "Improve attendance to reach safer academic standing.",
            "Try to maintain at least 75% attendance consistently."
        ]
    else:
        dynamic += [
            "Good attendance maintained. Keep it consistent.",
            "Regular class participation is helping your performance."
        ]

    # Marks logic
    if avg_marks < 40:
        dynamic += [
            "Your marks are below passing level. Focus on core concepts.",
            "Increase practice and revision immediately."
        ]
    elif avg_marks < 60:
        dynamic += [
            "Your marks are average. Improve problem-solving practice.",
            "Focus on weak subjects to boost performance."
        ]
    else:
        dynamic += [
            "Strong academic performance observed.",
            "You can aim for distinction with consistent effort."
        ]

    # Backlogs logic
    if backlogs > 0:
        dynamic += [
            f"You have {backlogs} backlog(s). Prioritize clearing them.",
            "Backlogs will increase academic pressure if ignored."
        ]
    else:
        dynamic += [
            "No backlogs detected. Good academic standing.",
            "Maintain this consistency moving forward."
        ]

    # ===============================
    # FINAL OUTPUT
    # ===============================
    recommendations = list(dict.fromkeys(base + dynamic))[:8]

    return {
        "performance_level": performance,
        "risk_level": risk,
        "student_recommendations": recommendations
    }