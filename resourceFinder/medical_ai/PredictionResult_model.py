# resourceFinder/medical_ai/PredictionResult_model.py
from mongoengine import Document, StringField, ListField, DateTimeField, ReferenceField
import datetime
from resourceFinder.medical_ai.userModel import User  # Lazy import if circular issue

class PredictionResult(Document):
    user = ReferenceField(User, required=True)  # Reference to User instead of just user_id
    symptoms = ListField(StringField())
    location = StringField()
    diagnosis = StringField()
    recommended_doctors = ListField(StringField())
    medical_supplies = ListField(StringField())
    medical_resources = ListField(StringField())
    recommended_hospitals = ListField(StringField())
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "user_id": str(self.user.id),  # Convert ObjectId to string
            "symptoms": self.symptoms,
            "location": self.location,
            "diagnosis": self.diagnosis,
            "recommended_doctors": self.recommended_doctors,
            "medical_supplies": self.medical_supplies,
            "medical_resources": self.medical_resources,
            "recommended_hospitals": self.recommended_hospitals,
            "created_at": self.created_at.isoformat()
        }
