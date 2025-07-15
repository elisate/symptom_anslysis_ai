from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from resourceFinder.medical_ai.appointmentModel import Appointment
from resourceFinder.medical_ai.treatmentModel import Treatment
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.utility.email_sender import send_email  # Email utility


@csrf_exempt
def create_treatment(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)

    try:
        data = json.loads(request.body)

        # Get the appointment  make sure on this
        appointment = Appointment.objects.get(id=data['appointment_id'])

        # Get doctor from appointment
        doctor = appointment.doctor or request.user

        # Get the patient using appointment user
        patient = Patient.objects(user=appointment.user).first()
        if not patient:
            return JsonResponse({"error": "Patient record not found for this user"}, status=400)

        # Create treatment with national_id included
        treatment = Treatment(
            doctor=doctor,
            patient=patient,
            appointment=appointment,
            national_id=patient.national_id,  # ✅ Include national ID
            symptoms=data.get('symptoms', []),
            diagnosis=data['diagnosis'],
            prescription=data['prescription'],
            notes=data.get('notes', '')
        )
        treatment.save()

        # Add treatment to patient's treatment history
        patient.treatments.append(treatment)

        # Optionally add diagnosis to ongoing treatments
        if treatment.diagnosis and treatment.diagnosis not in patient.ongoing_treatments:
            patient.ongoing_treatments.append(treatment.diagnosis)

        patient.save()

        # Send Consultation Summary Email
        user = appointment.user
        hospital = appointment.hospital
        symptoms = ", ".join(data.get('symptoms', [])) if isinstance(data.get('symptoms'), list) else data.get('symptoms')

        subject = "Your Consultation Summary"
        message = f"""
        <div style="font-family: Arial, sans-serif; color: #333;">
          <div style="background-color: #3B82F6; padding: 20px; color: white; text-align: center;">
            <h1 style="margin: 0;">Consultation Summary</h1>
          </div>

          <div style="padding: 20px;">
            <p>Dear <strong>{user.firstname} {user.lastname}</strong>,</p>

            <p>
              Thank you for attending your consultation at <strong>{hospital.hospital_name}</strong> on 
              <strong>{appointment.date} ({appointment.day})</strong> from 
              <strong>{appointment.start_time}</strong> to <strong>{appointment.end_time}</strong>.
            </p>

            <p>Below is a summary of your consultation:</p>

            <ul style="line-height: 1.6;">
              <li><strong>Symptoms:</strong> {symptoms}</li>
              <li><strong>Diagnosis:</strong> {treatment.diagnosis}</li>
              <li><strong>Prescription:</strong> {treatment.prescription}</li>
              <li><strong>Additional Notes:</strong> {treatment.notes or "N/A"}</li>
            </ul>

            <p>If you have any follow-up concerns or questions, please feel free to reach out to us.</p>
            <p>Contact: +250 787 239 952</p>

            <p style="margin-top: 30px;">Best regards,<br><strong>MediConnect AI-RWA-CST Team</strong></p>
          </div>

          <div style="background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #888;">
            © 2025 MediConnect AI-RWA-CST. All rights reserved.
          </div>
        </div>
        """

        send_email(to_email=user.email, subject=subject, message=message)

        return JsonResponse({"message": "Treatment created and email sent successfully."})

    except Appointment.DoesNotExist:
        return JsonResponse({"error": "Appointment not found."}, status=404)
    except KeyError as ke:
        return JsonResponse({"error": f"Missing field: {str(ke)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
