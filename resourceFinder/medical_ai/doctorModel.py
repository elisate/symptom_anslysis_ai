from mongoengine import Document, StringField, ListField, ReferenceField
from resourceFinder.medical_ai.userModel import User

class Doctor(Document):
    user = ReferenceField(User, required=True, unique=True)
    full_name = StringField(required=False)
    age = StringField()
    gender = StringField(choices=["Male", "Female", "Other"])
    profile_image_url = StringField()  # <-- store Cloudinary URL here
    phone = StringField()
    email = StringField()
    notes = StringField()
    
    specialty = StringField()
    certifications = ListField(StringField())
    available_times = ListField(StringField())

    hospital = ReferenceField('Hospital', required=False)

    def get_user_email(self):
        return self.user.email if self.user else None

    def get_full_name(self):
        return self.full_name
