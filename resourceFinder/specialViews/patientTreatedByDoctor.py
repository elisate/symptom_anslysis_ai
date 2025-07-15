from bson import ObjectId
from django.http import JsonResponse
from resourceFinder.medical_ai.treatmentModel import Treatment
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.doctorModel import Doctor

def patients_and_treatments_by_doctor(request, doctor_id):
    from bson import ObjectId
    from django.http import JsonResponse
    from resourceFinder.medical_ai.treatmentModel import Treatment
    from resourceFinder.medical_ai.patientModel import Patient
    from resourceFinder.medical_ai.doctorModel import Doctor

    try:
        doctor_obj_id = ObjectId(doctor_id)
    except:
        return JsonResponse({"error": "Invalid doctor ID"}, status=400)

    # FIX 1: Search Doctor by `user` reference, not `id`
    doctor = Doctor.objects(user=doctor_obj_id).first()
    if not doctor:
        return JsonResponse({"patients": [], "message": "Doctor not found."}, status=404)

    treatments = Treatment.objects(doctor=doctor.user.id)

    if not treatments:
        return JsonResponse({"patients": [], "message": "No treatments found for this doctor."})

    patient_map = {}
    for treatment in treatments:
        if not treatment.patient:
            continue

        pid = str(treatment.patient.id)
        if pid not in patient_map:
            patient_map[pid] = {
                "patient": treatment.patient,
                "treatments": []
            }
        patient_map[pid]["treatments"].append(treatment)

    response_data = []
    for entry in patient_map.values():
        patient = entry["patient"]
        treatment_list = entry["treatments"]

        user = patient.user
        full_name = f"{user.firstname} {user.lastname}" if user else "Unknown"

        # FIX 2: Safe hospital access
        patient_data = {
            "id": str(patient.id),
            "full_name": full_name,
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone,
            "hospital": str(patient.hospital) if patient.hospital else None,
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

        for t in treatment_list:
            patient_data["treatments"].append({
                "id": str(t.id),
                "appointment_id": str(t.appointment.id) if t.appointment else None,
                "symptoms": t.symptoms,
                "diagnosis": t.diagnosis,
                "prescription": t.prescription,
                "notes": t.notes,
                "created_at": t.created_at.isoformat()
            })

        response_data.append(patient_data)

    return JsonResponse({"patients": response_data})
