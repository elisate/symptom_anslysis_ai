import joblib
from .models import PredictionTable
import pandas as pd
import os

# Load trained model
# model = joblib.load(r"C:\Users\user\Desktop\FINAL YEAR PRO CODE\finalp\resourceFinder\medical_ai\diagnosis_model.pkl")


from django.conf import settings


model_path = os.path.join(settings.BASE_DIR, 'resourceFinder', 'medical_ai', 'diagnosis_model.pkl')
model = joblib.load(model_path)

def predict_diagnosis(user, symptoms, location):
    """
    Predict diagnosis and save prediction data in MongoDB.
    
    :param user: User ID
    :param symptoms: List of symptoms
    :param location: User's location
    :return: PredictionTable record (saved in MongoDB)
    """
    try:
        # Convert symptoms list to a string
        symptoms_str = ", ".join(symptoms).lower()

        # AI Prediction
        predicted_diagnosis = model.predict([symptoms_str])[0]

        # Find recommendations from dataset
        recommended_doctors = []
        medical_supplies = []
        medical_resources = []
        recommended_hospitals=[]

        # Open CSV and fetch recommended data
        file_path = os.path.join(os.path.dirname(__file__), "health_dataset.csv")
        
        # Check if the file exists before reading it
        if os.path.exists(file_path):
            data = pd.read_csv(file_path)
        else:
            return {"error": "Dataset file not found."}

        # Match diagnosis
        match = data[data['Diagnosis'].str.lower() == predicted_diagnosis.lower()]

        if not match.empty:
            recommended_doctors = match['Recommended_Doctors'].values[0].split(", ")
            medical_supplies = match['Medical_Supplies'].values[0].split(", ")
            medical_resources = match['Medical_Resources'].values[0].split(", ")
            recommended_hospitals = match['Recommended_Hospitals'].values[0].split(", ")
        else:
            return {"error": "Diagnosis not found in dataset."}

        # Create and save patient record in MongoDB
        predictionTable = PredictionTable(
            user=user,
            symptoms=symptoms_str,
            location=location,
            diagnosis=predicted_diagnosis,
            recommended_doctors=recommended_doctors,
            medical_supplies=medical_supplies,
            medical_resources=medical_resources,
            recommended_hospitals=recommended_hospitals
        )
        predictionTable.save()

        return {
            "prediction_id": str(predictionTable.id),
            "user": str(user),
            "diagnosis": predicted_diagnosis,
            "recommended_doctors": recommended_doctors,
            "medical_supplies": medical_supplies,
            "medical_resources": medical_resources,
            "recommended_hospitals":recommended_hospitals
        }

    except Exception as e:
        return {"error": str(e)}
