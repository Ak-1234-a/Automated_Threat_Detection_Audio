import pandas as pd
import numpy as np
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_class_weight

# Load dataset
data = pd.read_csv("TEL Corpus --  Spreadsheet version.csv")

# Normalize column names
data.columns = data.columns.str.strip().str.lower()

# Ensure correct column names
if 'text' not in data.columns or 'label' not in data.columns:
    raise KeyError("Dataset must contain 'text' and 'label' columns. Found: " + str(data.columns))

# Drop missing values
data = data[['text', 'label']].dropna()

# Preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text

data['text'] = data['text'].apply(preprocess_text)

# Convert categorical labels to numerical values
label_mapping = {"Safe": 0, "Threat": 1, "Offensive": 2}
data['label'] = data['label'].map(label_mapping)

# Drop any rows where mapping failed
data = data.dropna()
data['label'] = data['label'].astype(int)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(data['text'], data['label'], test_size=0.2, random_state=42)

# Compute class weights to handle imbalance
class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
class_weight_dict = {i: class_weights[i] for i in range(len(class_weights))}

# Create a pipeline with TF-IDF and Logistic Regression
model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=5000, stop_words='english')),
    ('classifier', LogisticRegression(class_weight='balanced'))
])

# Train model
model_pipeline.fit(X_train, y_train)

# Evaluate model
y_pred = model_pipeline.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred, zero_division=0))

# Save model
joblib.dump(model_pipeline, "threat_model.pkl")
print("Model saved as 'threat_model.pkl'")
