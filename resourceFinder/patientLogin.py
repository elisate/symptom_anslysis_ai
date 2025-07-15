from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.doctorModel import Doctor
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.utility.jwt_utils import generate_jwt_token
from bson import ObjectId
import json

def get_role_data(obj):
    """Extracts and converts only the id and user fields."""
    if not obj:
        return None
    return {
        "id": str(obj.id),
        "user": str(obj.user.id)
    }

@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        user = User.objects(email=email).first()

        if not user or not check_password(password, user.password):
            return JsonResponse({"error": "Invalid email or password"}, status=401)

        token = generate_jwt_token(user)

        user_data = {
            "user_id": str(user.id),
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "national_id":user.national_id,
            "userRole": user.userRole
        }

        role_data = None

        if user.userRole == UserRole.DOCTOR.value:
            doctor = Doctor.objects(user=user).first()
            role_data = get_role_data(doctor)

        elif user.userRole == UserRole.HOSPITAL.value:
            hospital = Hospital.objects(user=user).first()
            role_data = get_role_data(hospital)

        elif user.userRole == UserRole.PATIENT.value:
            patient = Patient.objects(user=user).first()
            role_data = get_role_data(patient)

        return JsonResponse({
            "token": token,
            "user": user_data,
            "role_data": role_data
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
