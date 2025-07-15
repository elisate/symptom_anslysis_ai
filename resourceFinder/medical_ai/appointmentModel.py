from mongoengine import Document, ReferenceField, DateTimeField, StringField, DateField
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
import datetime

class Appointment(Document):
    user = ReferenceField(User, required=True)         # Patient/user who made the appointment
    hospital = ReferenceField(Hospital, required=True) # Hospital for the appointment
    prediction = ReferenceField(PredictionResult, required=True) # AI diagnosis reference

    doctor = ReferenceField(User, required=False)      # Assigned doctor (new field)

    day = StringField(required=True, choices=[
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ])
    date = DateField(required=True)
    start_time = StringField(required=True)
    end_time = StringField(required=True)

    status = StringField(default="pending", choices=[
        "pending", "approved", "rejected", "completed", "assigned"
    ])

    created_at = DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f"Appointment for {self.user} at {self.hospital.name} on {self.date} ({self.day})"
