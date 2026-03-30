import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score


def train():

    # Load dataset
    dataset_path = os.path.join(
        os.path.dirname(__file__),
        "dataset",
        "student_dataset.csv"
    )

    df = pd.read_csv(dataset_path)

    # Features and label
    X = df[["attendance", "internal_marks", "assignment_score", "backlogs"]]
    y = df["performance"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Train model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Test accuracy
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    # Save model
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    print("Model and Scaler saved successfully!")


if __name__ == "__main__":
    train()
