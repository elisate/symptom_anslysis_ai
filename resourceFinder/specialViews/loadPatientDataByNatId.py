from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from bson import ObjectId
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.treatmentModel import Treatment

@csrf_exempt
def load_patient_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        national_id = data.get("national_id")

        if not national_id:
            return JsonResponse({"error": "national_id is required"}, status=400)

        # Find patient by national_id
        patient = Patient.objects(national_id=national_id).first()
        if not patient:
            return JsonResponse({"error": "No patient found with this national ID"}, status=404)

        # Find all treatments linked to this patient by patient ObjectId
        treatments = Treatment.objects(patient=patient.id)

        # Build response with patient info and treatments
        response = {
            "patient": {
                "patient_id": str(patient.id),
                "firstname": patient.firstname,
                "lastname": patient.lastname,
                "national_id": patient.national_id,
                "gender": patient.gender,
                "age": patient.age,
                "phone": patient.phone,
                "height_cm": patient.height_cm,
                "weight_kg": patient.weight_kg,
                "profile_image": patient.profile_image,
                "treatments": [
                    {
                        "treatment_id": str(t.id),
                        "doctor": {
                            "id": str(t.doctor.id),
                            "name": f"{t.doctor.firstname} {t.doctor.lastname}"
                        },
                        "appointment": str(t.appointment.id) if t.appointment else None,
                        "symptoms": t.symptoms,
                        "diagnosis": t.diagnosis,
                        "prescription": t.prescription,
                        "notes": t.notes,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in treatments
                ]
            }
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        # Log e if needed for debugging
        return JsonResponse({"error": str(e)}, status=500)


def patient_info_and_treatments(request, patient_id):
    try:
        patient_obj_id = ObjectId(patient_id)
    except:
        return JsonResponse({"error": "Invalid patient ID"}, status=400)

    # Fetch patient
    try:
        patient = Patient.objects.get(id=patient_obj_id)
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Patient not found"}, status=404)

    # Fetch treatments for the patient
    treatments = Treatment.objects(patient=patient_obj_id)

    user = patient.user
    full_name = f"{user.firstname} {user.lastname}" if user else "Unknown"

    patient_data = {
        "id": str(patient.id),
        "full_name": full_name,
        "age": patient.age,
        "gender": patient.gender,
        "phone": patient.phone,
        "hospital": patient.hospital.name if patient.hospital else None,
        "national_id": patient.national_id,
        "profile_image": patient.profile_image,
        "height_cm": patient.height_cm,
        "weight_kg": patient.weight_kg,
        "medical_history": patient.medical_history,
        "allergies": patient.allergies,
        "ongoing_treatments": patient.ongoing_treatments,
        "emergency_contact": patient.emergency_contact,
        "treatments": []
    }

    for treatment in treatments:
        patient_data["treatments"].append({
            "id": str(treatment.id),
            "appointment_id": str(treatment.appointment.id) if treatment.appointment else None,
            "symptoms": treatment.symptoms,
            "diagnosis": treatment.diagnosis,
            "prescription": treatment.prescription,
            "notes": treatment.notes,
            "created_at": treatment.created_at.isoformat()
        })

    return JsonResponse(patient_data)



def get_patient_by_national_id(request, national_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed"}, status=405)

    try:
        # Find patient by national_id (string), no ObjectId conversion
        patient = Patient.objects.get(national_id=national_id)

        treatments = Treatment.objects(patient=patient.id)

        response_data = {
            "patient": {
                "patient_id": str(patient.id),
                "firstname": patient.firstname,
                "lastname": patient.lastname,
                "national_id": patient.national_id,
                "gender": patient.gender,
                "age": patient.age,
                "phone": patient.phone,
                "height_cm": patient.height_cm,
                "weight_kg": patient.weight_kg,
                "profile_image": patient.profile_image,
                "treatments": [
                    {
                        "treatment_id": str(t.id),
                        "doctor": {
                            "id": str(t.doctor.id),
                            "name": f"{t.doctor.firstname} {t.doctor.lastname}"
                        } if t.doctor else None,
                        "appointment": str(t.appointment.id) if t.appointment else None,
                        "symptoms": t.symptoms,
                        "diagnosis": t.diagnosis,
                        "prescription": t.prescription,
                        "notes": t.notes,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in treatments
                ]
            }
        }

        return JsonResponse(response_data, status=200)

    except Patient.DoesNotExist:
        return JsonResponse({"error": "Patient not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_patient_by_id(request, patient_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed"}, status=405)

    try:
        patient = Patient.objects.get(id=ObjectId(patient_id))
        treatments = Treatment.objects(patient=patient.id)

        response_data = {
            "patient": {
                "patient_id": str(patient.id),
                "firstname": patient.firstname,
                "lastname": patient.lastname,
                "national_id": patient.national_id,
                "gender": patient.gender,
                "age": patient.age,
                "phone": patient.phone,
                "height_cm": patient.height_cm,
                "weight_kg": patient.weight_kg,
                "profile_image": patient.profile_image,
                "treatments": [
                    {
                        "treatment_id": str(t.id),
                        "doctor": {
                            "id": str(t.doctor.id),
                            "name": f"{t.doctor.firstname} {t.doctor.lastname}"
                        } if t.doctor else None,
                        "appointment": str(t.appointment.id) if t.appointment else None,
                        "symptoms": t.symptoms,
                        "diagnosis": t.diagnosis,
                        "prescription": t.prescription,
                        "notes": t.notes,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in treatments
                ]
            }
        }

        return JsonResponse(response_data, status=200)

    except Patient.DoesNotExist:
        return JsonResponse({"error": "Patient not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)