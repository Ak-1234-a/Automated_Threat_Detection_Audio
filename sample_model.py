# sample_model.py (Training script)
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
df = pd.read_csv("TEL Corpus --  Spreadsheet version.csv")

# Prepare data
X = df["Text"]  # Transcribed text
y = df["Label"]  # Threat classification

# Convert text to numerical features using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
X_tfidf = vectorizer.fit_transform(X)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Train Logistic Regression model
model = LogisticRegression(max_iter=1000, class_weight={"Offensive": 3, "Threat": 2, "Safe": 1}, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"Model Accuracy: {accuracy * 100:.2f}%")
print(report)

# Save the model and vectorizer
joblib.dump(model, "threat_detection_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")