import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# Load dataset
data = pd.read_csv("health_dataset.csv")

# Convert symptoms to lowercase for consistency
data['Symptoms'] = data['Symptoms'].str.lower()

# Train AI Model
X = data['Symptoms']
y = data['Diagnosis']

model = make_pipeline(CountVectorizer(), MultinomialNB())
model.fit(X, y)

# Save the model
joblib.dump(model, "diagnosis_model.pkl")

print(" Model trained and saved as diagnosis_model.pkl")
