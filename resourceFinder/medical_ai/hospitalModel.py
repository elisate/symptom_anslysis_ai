from mongoengine import Document, StringField, ListField, ReferenceField, EmailField
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.doctorModel import Doctor
from resourceFinder.medical_ai.patientModel import Patient

class Hospital(Document):
    user = ReferenceField(User, required=True, unique=True)
    hospital_name = StringField(required=True, unique=True)
    location = StringField(required=True)
    contact = StringField()
    email = EmailField()
    Medical_Supplies = ListField(StringField())
    Medical_Resources = ListField(StringField())
    doctors_assigned = ListField(ReferenceField(Doctor))

    # Optional list of assigned patients for quick access
    patients_assigned = ListField(ReferenceField(Patient))

    meta = {
        'collection': 'hospitals',
        'ordering': ['hospital_name']
    }

    def __str__(self):
        return self.hospital_name

    def get_doctor_names(self):
        return [f"{doc.user.firstname} {doc.user.lastname}" for doc in self.doctors_assigned if doc.user]

    def get_patient_names(self):
        return [patient.get_full_name() for patient in self.patients_assigned]
