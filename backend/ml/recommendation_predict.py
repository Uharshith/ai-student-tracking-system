import os
import joblib
import numpy as np

BASE_DIR = os.path.dirname(__file__)
model_path = os.path.join(BASE_DIR, "recommendation_model.pkl")

model = joblib.load(model_path)

messages = {
    "GOOD_PROGRESS": "Maintain your current academic performance.",
    "IMPROVE_ATTENDANCE": "Improve your attendance to enhance learning.",
    "FOCUS_MIDTERM": "Focus on improving midterm preparation.",
    "FOCUS_INTERNAL": "Work more on internal assessments.",
    "FOCUS_FINAL": "Prepare better for final exams.",
    "GENERAL_IMPROVEMENT": "Overall academic improvement is required."
}

def get_recommendation(attendance, mid, internal, final, avg):

    data = np.array([[attendance, mid, internal, final, avg]])

    prediction = model.predict(data)[0]

    return messages[prediction]