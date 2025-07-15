from mongoengine import Document, ReferenceField, ListField, StringField, EmbeddedDocument, EmbeddedDocumentField
from resourceFinder.medical_ai.hospitalModel import Hospital

# Create an EmbeddedDocument class for TimeSlot
class TimeSlot(EmbeddedDocument):
    start_time = StringField(required=True)
    end_time = StringField(required=True)
    date = StringField(required=True)  # You can also use DateTimeField if you prefer

class HospitalSchedule(Document):
    hospital = ReferenceField(Hospital, required=True, unique=True)
    monday = ListField(EmbeddedDocumentField(TimeSlot))
    tuesday = ListField(EmbeddedDocumentField(TimeSlot))
    wednesday = ListField(EmbeddedDocumentField(TimeSlot))
    thursday = ListField(EmbeddedDocumentField(TimeSlot))
    friday = ListField(EmbeddedDocumentField(TimeSlot))
    saturday = ListField(EmbeddedDocumentField(TimeSlot))
    sunday = ListField(EmbeddedDocumentField(TimeSlot))
