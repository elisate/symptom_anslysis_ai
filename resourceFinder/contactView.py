from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.html import escape
from mongoengine.errors import ValidationError
import json

from resourceFinder.medical_ai.contactModel import Contact
from resourceFinder.utility.email_sender import send_email


@csrf_exempt
def createContact(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        full_name = data.get("full_name")
        email = data.get("email")
        content = data.get("content")

        if not all([full_name, email, content]):
            return JsonResponse({"error": "All fields are required"}, status=400)

        # Save contact
        contact = Contact(
            full_name=full_name,
            email=email,
            content=content
        )
        contact.save()

        # Confirmation email content
        thank_you_html = f"""
        <div style="font-family: Arial, sans-serif; color: #333;">
          <!-- Header -->
          <div style="background-color: #3B82F6; padding: 20px; color: white; text-align: center;">
            <h1 style="margin: 0;">Thank You for Contacting MediConnect AI-RWA-CST</h1>
          </div>

          <!-- Body -->
          <div style="padding: 20px;">
            <p>Dear <strong>{escape(full_name)}</strong>,</p>

            <p>
              Thank you for reaching out to <strong>MediConnect AI-RWA-CST</strong>. 
              We appreciate your time and effort in contacting us.
            </p>

            <p>
              Your message has been successfully received and is currently being reviewed by our support team.
              We strive to respond promptly and address your inquiry thoroughly.
            </p>

            <p>
              If your request is urgent, please don’t hesitate to call us directly at 
              <strong style="color: #3B82F6;">+250 787 239 952</strong>.
            </p>

            <p style="margin-top: 20px;">
              Thank you once again for connecting with us. We’re here to help you.
            </p>

            <p style="margin-top: 30px;">
              Best regards,<br>
              <strong>The MediConnect AI-RWA-CST Support Team</strong>
            </p>
          </div>

          <!-- Footer -->
          <div style="background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #888;">
            © 2025 MediConnect AI-RWA-CST. All rights reserved.
          </div>
        </div>
        """

        # Send confirmation email
        send_email(
            to_email=email,
            subject="Thank You for Contacting Mediconnect AI-RWA",
            message=thank_you_html
        )

        return JsonResponse({"message": "Contact saved and email sent successfully."}, status=201)

    except (json.JSONDecodeError, ValidationError) as e:
        return JsonResponse({"error": f"Invalid input: {str(e)}"}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
