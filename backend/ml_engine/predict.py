import os
import joblib
import numpy as np
import pandas as pd 


# Load model and scaler once (not every function call)
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)


def predict_performance(attendance, internal_marks, assignment_score, backlogs):

    input_data = pd.DataFrame([{
        "attendance": attendance,
        "internal_marks": internal_marks,
        "assignment_score": assignment_score,
        "backlogs": backlogs
    }])

    scaled_input = scaler.transform(input_data)
    prediction = model.predict(scaled_input)

    return int(prediction[0])