import joblib
import numpy as np
import random

model = joblib.load("ml/trend_model.pkl")

def predict_trend(mid, internal, final):

    # normalize marks
    mid_pct = (mid / 30) * 100
    internal_pct = (internal / 30) * 100
    final_pct = (final / 70) * 100

    features = np.array([[mid_pct, internal_pct, final_pct]])

    prediction = model.predict(features)[0]

    declining_messages = [
        "Your performance trend shows a decline across exams. Focus on revisiting weak topics and strengthening core concepts.",
        "Recent exam scores are lower than earlier ones, indicating possible gaps in revision. Try solving more practice questions.",
        "A downward trend in marks suggests difficulties in recent assessments. Regular revision and concept review are recommended.",
        "Performance appears to be dropping across exams. Consider discussing challenging topics with faculty for better clarity.",
        "Declining scores indicate inconsistent preparation. Creating a structured study plan may help improve future results."
    ]

    improving_messages = [
        "Your academic performance shows steady improvement across exams. Your preparation strategy seems effective.",
        "Marks have increased across assessments, indicating stronger understanding and better exam readiness.",
        "Your results show a positive growth trend. Continued practice and revision should further improve performance.",
        "A clear improvement in marks suggests better concept clarity and consistent effort in preparation.",
        "Your exam scores are rising progressively. Maintaining the same study discipline will help sustain this progress."
    ]

    stable_messages = [
        "Your exam performance is relatively stable across assessments. Additional practice may help increase scores.",
        "Marks remain fairly consistent between exams, indicating steady understanding of the subject.",
        "Your performance trend is stable with minor fluctuations. Targeted revision could help boost results.",
        "Consistent exam scores show stable preparation, but further improvement is possible with deeper practice.",
        "Your academic performance shows moderate stability. Strengthening weaker areas could improve outcomes."
    ]

    if prediction == "Declining":
        message = random.choice(declining_messages)

    elif prediction == "Improving":
        message = random.choice(improving_messages)

    else:
        message = random.choice(stable_messages)

    return prediction, message