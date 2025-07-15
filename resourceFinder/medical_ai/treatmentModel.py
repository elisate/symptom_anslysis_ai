# treatmentModel.py
from mongoengine import Document, ReferenceField, StringField, DateTimeField, ListField
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.appointmentModel import Appointment
import datetime

class Treatment(Document):
    doctor = ReferenceField(User, required=True)
    patient = ReferenceField(Patient, required=True)
    appointment = ReferenceField(Appointment, required=True)
    
    # New field for national_id for easier querying
    national_id = StringField(required=True)

    symptoms = ListField(StringField()) 
    diagnosis = StringField(required=True)
    prescription = StringField(required=True)
    notes = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
