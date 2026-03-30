import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
df = pd.read_csv("corrected_trend_training_data_1000.csv")

# Features
X = df[["mid", "internal", "final"]]

# Target
y = df["trend"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Predictions
pred = model.predict(X_test)

# Accuracy
print("Trend Model Accuracy:", accuracy_score(y_test, pred))

# Detailed report
print(classification_report(y_test, pred))

# Save model
joblib.dump(model, "trend_model.pkl")

print("Trend model trained and saved successfully.")