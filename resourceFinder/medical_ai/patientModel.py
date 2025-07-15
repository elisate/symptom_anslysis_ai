from mongoengine import Document, StringField, ListField, ReferenceField
from resourceFinder.medical_ai.userModel import User

class Patient(Document):
    user = ReferenceField(User, required=True, unique=True)
    email = StringField()
    national_id = StringField(required=False, unique=True)
    profile_image = StringField()
    age = StringField()
    gender = StringField(choices=["Male", "Female", "Other"])
    phone = StringField()
    height_cm = StringField()
    weight_kg = StringField()
    firstname = StringField()
    lastname = StringField()
    
    # ✅ Safe circular reference via string
    hospital = ReferenceField('Hospital', required=False)
    assigned_hospitals = ListField(ReferenceField('Hospital'))  # ✅ Added for tracking

    medical_history = ListField(StringField())
    allergies = ListField(StringField())
    ongoing_treatments = ListField(StringField())
    emergency_contact = StringField()
    treatments = ListField(ReferenceField('Treatment'))

    def get_full_name(self):
        return f"{self.firstname} {self.lastname}"
