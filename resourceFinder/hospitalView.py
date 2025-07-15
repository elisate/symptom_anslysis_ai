from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from resourceFinder.medical_ai.hospitalModel import Hospital
from resourceFinder.medical_ai.userModel import User, UserRole
from mongoengine.errors import NotUniqueError, ValidationError
from django.conf import settings
from datetime import datetime
import json
import jwt

@csrf_exempt
def create_hospital(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            hospital_name = data["hospital_name"]
            email = data["email"].strip().lower()
            password = data["password"].strip()
            location = data["location"]
            contact = data.get("contact", "")
            supplies = data.get("Medical_Supplies", [])
            resources = data.get("Medical_Resources", [])

            # Check if email already exists
            if User.objects(email__iexact=email).first():
                return JsonResponse({"error": "User already exists with this email"}, status=400)

            # Hash the password
            hashed_password = make_password(password)

            # Create user (with role = hospital)
            user = User(
                hospitalName=hospital_name,
                email=email,
                password=hashed_password,
                userRole=UserRole.HOSPITAL.value
            )
            user.save()

            # Create hospital record
            hospital = Hospital(
                user=user,
                hospital_name=hospital_name,
                location=location,
                contact=contact,
                email=email,
                Medical_Supplies=supplies,
                Medical_Resources=resources
            )
            hospital.save()

            # Generate JWT token
            payload = {
                "user_id": str(user.id),
                "email": user.email,
                "userRole": user.userRole,
                "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
                "iat": datetime.utcnow()
            }

            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

            return JsonResponse({
                "message": "Hospital and user account created successfully.",
                "token": token,
                "user": {
                    "user_id": str(user.id),
                    "email": user.email,
                    "userRole": user.userRole,
                    "hospital_id": str(user.id)   # fixed here
                },
                "hospital": {
                    "hospital_id": str(hospital.id),
                    "hospital_name": hospital.hospital_name,
                    "location": hospital.location,
                    "contact": hospital.contact
                }
            }, status=201)

        except NotUniqueError:
            return JsonResponse({"error": "Hospital name or email already exists."}, status=400)
        except KeyError as e:
            return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)
        except ValidationError as ve:
            return JsonResponse({"error": str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def get_all_hospitals(request):
    if request.method == "GET":
        try:
            hospitals = Hospital.objects()  # Fetch all hospital records
            hospital_list = []

            for hospital in hospitals:
                hospital_list.append({
                    "hospital_id": str(hospital.id),
                    "hospital_name": hospital.hospital_name,
                    "location": hospital.location,
                    "contact": hospital.contact,
                    "email": hospital.email,
                    "Medical_Supplies": hospital.Medical_Supplies,
                    "Medical_Resources": hospital.Medical_Resources,
                })

            return JsonResponse({"hospitals": hospital_list}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
