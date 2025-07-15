from mongoengine import Document, StringField, ListField, ReferenceField
from resourceFinder.medical_ai.userModel import User  # Ensure lazy import if needed

class PredictionTable(Document):
    user = ReferenceField('User', required=True)
    symptoms = StringField()
    location = StringField()
    diagnosis = StringField()

    # Use ListField of StringField with default empty list to avoid null issues
    recommended_hospitals = ListField(StringField(), default=[])
    recommended_doctors = ListField(StringField(), default=[])
    medical_supplies = ListField(StringField(), default=[])
    medical_resources = ListField(StringField(), default=[])

    def get_user(self):
        from resourceFinder.medical_ai.userModel import User  # Lazy import to prevent circular import
        return self.user
