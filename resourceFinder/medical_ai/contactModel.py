from mongoengine import Document, StringField

class Contact(Document):
    full_name = StringField(required=True)
    email = StringField(required=True)
    content = StringField(required=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"
