from django.core.mail import EmailMessage
from django.conf import settings

def send_email(to_email, subject, message):
    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        print("✅ Email sent!")
    except Exception as e:
        print("❌ Email sending failed:", e)
