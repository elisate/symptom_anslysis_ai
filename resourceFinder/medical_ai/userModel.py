from mongoengine import Document, StringField, DateTimeField
from enum import Enum

# Define Enum for user roles
class UserRole(str, Enum):
    
    PATIENT = "patient"
    DOCTOR = "doctor"
    HOSPITAL = "hospital"
    SUPER_ADMIN="superadmin"

class User(Document):
    firstname = StringField(required=False)
    lastname = StringField(required=False)
    hospitalName = StringField(required=False)
    phone = StringField(required=False)
    email = StringField(required=True, unique=True)
    profile_image = StringField(require=False)
    password = StringField(required=True)
    national_id = StringField(required=False)  # ✅ required and unique
    reset_password_otp = StringField(required=False)
    reset_password_expiry = DateTimeField(required=False)
    userRole = StringField(
        choices=[role.value for role in UserRole],
        default=UserRole.PATIENT.value
    )

    # Lazy import of Patient when it's actually needed
    def get_patient(self):
        from resourceFinder.medical_ai.patientModel import Patient  # Lazy import to avoid circular import
        return Patient.objects(user=self).first()
