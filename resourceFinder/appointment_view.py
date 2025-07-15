from django.http import JsonResponse
import traceback
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from resourceFinder.medical_ai.userModel import User
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.scheduleModel import HospitalSchedule
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
from resourceFinder.medical_ai.appointmentModel import Appointment
from bson.objectid import ObjectId, InvalidId
from mongoengine.errors import DoesNotExist
from resourceFinder.utility.email_sender import send_email
from rest_framework.decorators import api_view
from django.utils.dateformat import format as date_format
from resourceFinder.medical_ai.doctorModel import Doctor
from resourceFinder.medical_ai.patientModel import Patient

@csrf_exempt
def request_hospital_appointment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        user_id = getattr(request, "user_id", None)
        if not user_id:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        data = json.loads(request.body)
        hospital_name = data.get("hospital_name")
        appointment_datetime_str = data.get("appointment_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if not hospital_name or not appointment_datetime_str:
            return JsonResponse({"error": "hospital_name and appointment_date are required"}, status=400)

        user = User.objects(id=user_id).first()
        hospital = Hospital.objects(hospital_name=hospital_name).first()
        prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

        # ✅ Create patient if missing
        patient = Patient.objects(user=user).first()
        if not patient:
            patient = Patient(
                user=user,
                national_id=user.national_id,
                firstname=user.firstname,
                lastname=user.lastname,
                email=user.email
            )
            patient.save()

        if not all([user, hospital, prediction]):
            return JsonResponse({"error": "Missing user, hospital, or prediction"}, status=404)

        appointment_dt = datetime.fromisoformat(appointment_datetime_str)
        day_name = appointment_dt.strftime("%A").lower()

        if not start_time:
            start_time = appointment_dt.strftime("%H:%M")
        if not end_time:
            temp_dt = appointment_dt + timedelta(minutes=30)
            end_time = temp_dt.strftime("%H:%M")

        appointment = Appointment(
            user=user,
            hospital=hospital,
            prediction=prediction,
            day=day_name,
            date=appointment_dt.date(),
            start_time=start_time,
            end_time=end_time,
            status="pending"
        )
        appointment.save()

        # ✅ Assign hospital to patient
        if hospital not in patient.assigned_hospitals:
            patient.assigned_hospitals.append(hospital)
            patient.save()

        if patient not in hospital.patients_assigned:
            hospital.patients_assigned.append(patient)
            hospital.save()

        return JsonResponse({
            "message": "Appointment booked successfully",
            "appointment": {
                "id": str(appointment.id),
                "user": str(user.id),
                "hospital": hospital.hospital_name,
                "day": appointment.day,
                "date": str(appointment.date),
                "time": f"{appointment.start_time} - {appointment.end_time}",
                "status": appointment.status
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
@csrf_exempt
def get_appointments_by_hospital(request, hospital_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed"}, status=405)

    try:
        hospital = Hospital.objects(id=hospital_id).first()
        if not hospital:
            return JsonResponse({"error": "Hospital not found"}, status=404)

        # Pagination: 5 rows per page
        page = int(request.GET.get("page", 1))
        rows_per_page = 5
        skip = (page - 1) * rows_per_page

        # Query appointments
        all_appointments = Appointment.objects(hospital=hospital).order_by("-date")
        total_appointments = all_appointments.count()
        total_pages = (total_appointments + rows_per_page - 1) // rows_per_page

        appointments = all_appointments.skip(skip).limit(rows_per_page)

        result = []
        for appointment in appointments:
            user = appointment.user
            prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

            result.append({
                "appointment_id": str(appointment.id),
                "firstname": getattr(user, "firstname", "N/A"),
                "lastname": getattr(user, "lastname", "N/A"),
                "national_id": getattr(user, "national_id", "N/A"),
                "email": getattr(user, "email", "N/A"),
                "phone": getattr(user, "phone", "N/A"),
                "diagnosis": getattr(prediction, "diagnosis", "Not available") if prediction else "Not available",
                "date": str(appointment.date),
                "day": appointment.day,
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "status": appointment.status
            })

        return JsonResponse({
            "appointments": result,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_appointments": total_appointments,
                "rows_per_page": rows_per_page
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
 


@csrf_exempt
def get_appointments_by_user_id(request, user_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed"}, status=405)

    try:
        # Validate user_id format
        try:
            user_object_id = ObjectId(user_id)
        except InvalidId:
            return JsonResponse({"error": "Invalid user ID format"}, status=400)

        # Pagination parameters from query params
        try:
            page = int(request.GET.get("page", 1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        page_size = 5  # fixed page size

        # Calculate skip count
        skip = (page - 1) * page_size

        # Query total count for pagination info
        total_appointments = Appointment.objects(user=user_object_id).count()

        # Query appointments with skip and limit for pagination
        appointments = (
            Appointment.objects(user=user_object_id)
            .order_by("-date")
            .skip(skip)
            .limit(page_size)
        )

        result = []
        for appointment in appointments:
            hospital_name = "Unknown Hospital"
            try:
                if appointment.hospital:
                    hospital_name = appointment.hospital.hospital_name
            except Exception:
                pass

            result.append({
                "appointment_id": str(appointment.id),
                "hospital_name": hospital_name,
                "day": appointment.day,
                "date": str(appointment.date),
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "status": appointment.status,
                "created_at": appointment.created_at.isoformat(),
                "prediction_id": str(appointment.prediction.id) if appointment.prediction else "N/A",
                "user_id": str(user_object_id),
            })

        return JsonResponse({
            "appointments": result,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_appointments": total_appointments,
                "total_pages": (total_appointments + page_size - 1) // page_size,
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
    


@csrf_exempt
def get_all_pending_appointments_by_hospital(request, hospital_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed"}, status=405)

    try:
        hospital = Hospital.objects(id=hospital_id).first()
        if not hospital:
            return JsonResponse({"error": "Hospital not found"}, status=404)

        # Get all appointments with status 'pending'
        pending_appointments = Appointment.objects(
            hospital=hospital,
            status="pending"
        ).order_by("-date")

        result = []
        for appointment in pending_appointments:
            user = appointment.user
            prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

            result.append({
                "appointment_id": str(appointment.id),
                "firstname": getattr(user, "firstname", "N/A"),
                "lastname": getattr(user, "lastname", "N/A"),
                "national_id": getattr(user, "national_id", "N/A"),
                "email": getattr(user, "email", "N/A"),
                "phone": getattr(user, "phone", "N/A"),
                "diagnosis": getattr(prediction, "diagnosis", "Not available") if prediction else "Not available",
                "date": str(appointment.date),
                "day": appointment.day,
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "status": appointment.status
            })

        return JsonResponse({"appointments": result}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
def get_appointment_by_id(request, appointment_id):
    if request.method == 'GET':
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            user = appointment.user

            user_data = {
                "id": str(user.id),
                "firstname": user.firstname,
                "lastname": user.lastname,
                "hospitalName": user.hospitalName,
                "phone": user.phone,
                "email": user.email,
                "userRole": user.userRole,
            }

            return JsonResponse({
                "id": str(appointment.id),
                "user": user_data,
                "hospital": appointment.hospital.hospital_name,
                "prediction": str(appointment.prediction.id),
                "day": appointment.day,
                "date": appointment.date.strftime("%Y-%m-%d"),
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "status": appointment.status,
                "created_at": appointment.created_at.isoformat(),
            }, status=200)
        except DoesNotExist:
            return JsonResponse({"error": "Appointment not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def update_appointment_status(request, appointment_id):
    if request.method == 'PUT':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            new_status = body.get('status', '').lower()

            valid_statuses = ["pending", "approved", "rejected", "completed"]
            if new_status not in valid_statuses:
                return JsonResponse({"error": f"Invalid status. Must be one of {valid_statuses}"}, status=400)

            appointment = Appointment.objects.get(id=appointment_id)
            appointment.status = new_status
            appointment.save()

            # Extract appointment data for email
            user = appointment.user
            hospital = appointment.hospital

            user_email = user.email
            subject = "Your Appointment Status Has Been Updated"

            message = f"""
            <div style="font-family: Arial, sans-serif; color: #333;">
              <div style="background-color: #3B82F6; padding: 20px; color: white; text-align: center;">
                <h1 style="margin: 0;">Appointment Status Update</h1>
              </div>

              <div style="padding: 20px;">
                <p>Dear <strong>{user.firstname} {user.lastname}</strong>,</p>

                <p>
                  We want to inform you that your appointment at <strong>{hospital.hospital_name}</strong> 
                  on <strong>{appointment.date} ({appointment.day})</strong> from 
                  <strong>{appointment.start_time}</strong> to <strong>{appointment.end_time}</strong> has been updated.
                </p>

                <p>
                  <strong>New Status:</strong> 
                  <span style="color: #3B82F6; font-weight: bold;">{new_status.capitalize()}</span>
                </p>

                <p>
                  If you have any questions or concerns, feel free to contact us. 
                  Thank you for choosing our service.
                </p>

                <p style="margin-top: 30px;">Best regards,<br><strong>MediConnect AI-RWA-CST Team</strong></p>
              </div>

              <div style="background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #888;">
                © 2025 MediConnect AI-RWA-CST. All rights reserved.
              </div>
            </div>
            """

            send_email(to_email=user_email, subject=subject, message=message)

            return JsonResponse({
                "message": f"Appointment status updated to {new_status}",
                "appointment_id": str(appointment.id),
                "status": appointment.status
            }, status=200)

        except DoesNotExist:
            return JsonResponse({"error": "Appointment not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
@api_view(['POST'])
def assign_doctor_to_appointment(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        appointment_id = body.get('appointment_id')
        doctor_name = body.get('doctor_name')
        doctor_email_input = body.get('Email', '').strip()

        if not appointment_id or not doctor_name:
            return JsonResponse({"error": "Both appointment_id and doctor_name are required."}, status=400)

        # Get appointment
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return JsonResponse({"error": "Appointment not found."}, status=404)

        if appointment.status.lower() != "approved":
            return JsonResponse({"error": "Only appointments with 'approved' status can be assigned."}, status=400)

        # Parse doctor name
        try:
            first_name, last_name = doctor_name.strip().split(" ", 1)
        except ValueError:
            return JsonResponse({"error": "Doctor name must be in 'First Last' format."}, status=400)

        # Find doctor by name
        try:
            doctor = User.objects.get(firstname__iexact=first_name, lastname__iexact=last_name, userRole="doctor")
        except User.DoesNotExist:
            return JsonResponse({"error": "Doctor not found."}, status=404)

        # Assign doctor to appointment
        appointment.doctor = doctor
        appointment.status = "assigned"
        appointment.save()

        # Email to doctor
        doctor_subject = "New Appointment Assigned to You"
        doctor_message = f"""
        <div style="font-family: Arial, sans-serif; color: #333;">
          <div style="background-color: #10B981; padding: 20px; color: white; text-align: center;">
            <h1 style="margin: 0;">New Appointment Assigned</h1>
          </div>
          <div style="padding: 20px;">
            <p>Dear <strong>Dr. {doctor.firstname} {doctor.lastname}</strong>,</p>
            <p>You have been assigned an appointment with patient <strong>{appointment.user.firstname} {appointment.user.lastname}</strong>.</p>
            <p><strong>Date:</strong> {appointment.date} ({appointment.day})<br>
            <strong>Time:</strong> {appointment.start_time} - {appointment.end_time}<br>
            <strong>Hospital:</strong> {appointment.hospital.hospital_name if appointment.hospital else 'N/A'}</p>
            <p>Please check your dashboard for full details.</p>
            <p style="margin-top: 30px;">Best regards,<br><strong>MediConnect AI-RWA-CST Team</strong></p>
          </div>
          <div style="background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #888;">
            © 2025 MediConnect AI-RWA-CST. All rights reserved.
          </div>
        </div>
        """
        send_email(to_email=doctor.email, subject=doctor_subject, message=doctor_message)

        # Email to patient
        patient_subject = "Appointment Assigned to Doctor"
        patient_message = f"""
        <div style="font-family: Arial, sans-serif; color: #333;">
          <div style="background-color: #3B82F6; padding: 20px; color: white; text-align: center;">
            <h1 style="margin: 0;">Doctor Assigned</h1>
          </div>
          <div style="padding: 20px;">
            <p>Dear <strong>{appointment.user.firstname} {appointment.user.lastname}</strong>,</p>
            <p>Your appointment has been assigned to <strong>Dr. {doctor.firstname} {doctor.lastname}</strong> (<strong>{doctor.email}</strong>).</p>
            <p><strong>Date:</strong> {appointment.date} ({appointment.day})<br>
            <strong>Time:</strong> {appointment.start_time} - {appointment.end_time}<br>
            <strong>Hospital:</strong> {appointment.hospital.hospital_name if appointment.hospital else 'N/A'}</p>
            <p>Thank you for using MediConnect.</p>
            <p style="margin-top: 30px;">Best regards,<br><strong>MediConnect AI-RWA-CST Team</strong></p>
          </div>
          <div style="background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #888;">
            © 2025 MediConnect AI-RWA-CST. All rights reserved.
          </div>
        </div>
        """
        send_email(to_email=appointment.user.email, subject=patient_subject, message=patient_message)

        return JsonResponse({
            "message": "Doctor successfully assigned and notifications sent.",
            "appointment_id": str(appointment.id),
            "doctor_name": f"{doctor.firstname} {doctor.lastname}",
            "doctor_email": doctor.email,
            "status": appointment.status
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
def get_appointments_by_doctor_id(request, doctor_id):
    # Validate ObjectId
    if not ObjectId.is_valid(doctor_id):
        return JsonResponse({"error": "Invalid doctor ID."}, status=400)

    # Get the Doctor document
    doctor_doc = Doctor.objects(id=ObjectId(doctor_id)).first()
    if not doctor_doc:
        return JsonResponse({"error": "Doctor not found."}, status=404)

    # Get the actual User instance used in Appointment.doctor
    doctor_user = doctor_doc.user

    # Now use the User ID to find appointments
    appointments = Appointment.objects.filter(doctor=doctor_user).order_by('-date')

    result = []
    for appt in appointments:
        result.append({
            "appointment_id": str(appt.id),
            "date": appt.date.strftime("%Y-%m-%d") if appt.date else 'N/A',
            "day": appt.day,
            "start_time": appt.start_time,
            "end_time": appt.end_time,
            "status": appt.status,
            "created_at": appt.created_at.strftime("%Y-%m-%d %H:%M:%S") if appt.created_at else 'N/A',
            "patient": {
                "name": f"{appt.user.firstname} {appt.user.lastname}" if appt.user else 'N/A',
                "email": appt.user.email if appt.user else 'N/A',
                "phone": getattr(appt.user, 'phone', 'N/A') if appt.user else 'N/A',
                "role": appt.user.userRole if appt.user else 'N/A'
            },
            "hospital": appt.hospital.hospital_name if appt.hospital else 'N/A',
            "prediction_id": str(appt.prediction.id) if appt.prediction else 'N/A'
        })

    return JsonResponse({"appointments": result}, status=200)
