import pandas as pd
import numpy as np
import re
from imblearn.over_sampling import SMOTE
from sklearn.feature_extraction.text import TfidfVectorizer

# Load dataset
file_path = "TEL Corpus --  Spreadsheet version.csv"
data = pd.read_csv(file_path)

# Normalize column names
data.columns = data.columns.str.strip().str.lower()

# Ensure required columns exist
if 'text' not in data.columns or 'label' not in data.columns:
    raise KeyError("Dataset must contain 'text' and 'label' columns.")

# Drop missing values and duplicates
data = data[['text', 'label']].dropna().drop_duplicates()

# Preprocess text
def preprocess_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text

data['text'] = data['text'].apply(preprocess_text)

# Convert categorical labels to numerical values
label_mapping = {"Safe": 0, "Threat": 1, "Offensive": 2}
data['label'] = data['label'].map(label_mapping)

# Drop any unmapped rows
data = data.dropna()
data['label'] = data['label'].astype(int)

# Show class distribution before balancing
print("Before Balancing:")
print(data['label'].value_counts())

# Convert text to numerical features using TF-IDF (SMOTE works on numeric data)
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2), stop_words='english')
X_tfidf = vectorizer.fit_transform(data['text'])
y = data['label'].values

# Balance dataset using SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_tfidf, y)

# Convert back to DataFrame
balanced_texts = vectorizer.inverse_transform(X_resampled)
balanced_data = pd.DataFrame({'text': [' '.join(words) for words in balanced_texts], 'label': y_resampled})

# Convert labels back to original categories
inverse_label_mapping = {0: "Safe", 1: "Threat", 2: "Offensive"}
balanced_data['label'] = balanced_data['label'].map(inverse_label_mapping)

# Show class distribution after balancing
print("After Balancing:")
print(balanced_data['label'].value_counts())

# Save updated dataset
updated_file_path = "TEL_Corpus_Updated.csv"
balanced_data.to_csv(updated_file_path, index=False)

print(f"✅ Updated dataset saved as {updated_file_path}")
