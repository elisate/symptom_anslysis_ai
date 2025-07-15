from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.conf import settings
from resourceFinder.medical_ai.userModel import User, UserRole
from resourceFinder.medical_ai.patientModel import Patient
from resourceFinder.medical_ai.hospitalModel import Hospital
from datetime import datetime
import jwt
from bson import ObjectId
from resourceFinder.utility.cloudinary_helper import upload_image_to_cloudinary  # ✅ Use helper
from django.views.decorators.csrf import csrf_exempt
import json
@csrf_exempt
def create_patient(request):
    if request.method == 'POST':
        try:
            data = request.POST
            image = request.FILES.get('profile_image')
            if image is None:
                return JsonResponse({'error': 'Profile image is required'}, status=400)

            # Validate required fields
            required_fields = ['firstname', 'lastname', 'email', 'password', 'national_id']
            for field in required_fields:
                value = data.get(field, '').strip()
                if not value:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            email = data.get('email', '').strip().lower()
            password = data.get('password', '').strip()

            if User.objects(email__iexact=email).first():
                return JsonResponse({'error': 'User already exists with this email'}, status=400)

            hashed_password = make_password(password)

            user = User(
                firstname=data.get('firstname'),
                lastname=data.get('lastname'),
                email=email,
                password=hashed_password,
                userRole=UserRole.PATIENT.value
            )
            user.save()

            # ✅ Use Cloudinary helper to upload image
            image_url = upload_image_to_cloudinary(image)

            patient = Patient(
                user=user,
                national_id=data.get('national_id'),
                firstname=data.get('firstname'),
                lastname=data.get('lastname'),
                age=data.get('age'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                height_cm=data.get('height'),
                weight_kg=data.get('weight'),
                profile_image=image_url
            )

            hospital_id = data.get('hospital_id')
            if hospital_id:
                hospital = Hospital.objects(id=hospital_id).first()
                if not hospital:
                    return JsonResponse({'error': 'Hospital not found'}, status=404)
                patient.hospital = hospital

            patient.save()

            payload = {
                "user_id": str(user.id),
                "email": user.email,
                "userRole": user.userRole,
                "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
                "iat": datetime.utcnow()
            }
            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

            return JsonResponse({
                'message': 'Patient created successfully',
                'token': token,
                'user': {
                    'user_id': str(user.id),
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'email': user.email,
                    'userRole': user.userRole
                },
                'patient_id': str(patient.id)
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)



@csrf_exempt
def get_patients_by_hospital(request, hospital_id):
    if request.method == 'GET':
        try:
            # Validate hospital_id
            if not ObjectId.is_valid(hospital_id):
                return JsonResponse({'error': 'Invalid hospital ID'}, status=400)

            hospital = Hospital.objects(id=hospital_id).first()
            if not hospital:
                return JsonResponse({'error': 'Hospital not found'}, status=404)

            # Include both direct hospital and assigned_hospitals
            patients = Patient.objects.filter(
                __raw__={
                    "$or": [
                        {"hospital": hospital.id},
                        {"assigned_hospitals": hospital.id}
                    ]
                }
            )

            patient_list = []
            for patient in patients:
                patient_list.append({
                    'patient_id': str(patient.id),
                    'firstname': patient.firstname,
                    'lastname': patient.lastname,
                    'email': patient.user.email if patient.user else None,
                    'phone': patient.phone,
                    'age': patient.age,
                    'gender': patient.gender,
                    'profile_image': patient.profile_image,
                })

            return JsonResponse({'patients': patient_list}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET method is allowed'}, status=405)


csrf_exempt
def get_all_patients(request):
    if request.method == 'GET':
        try:
            patients = Patient.objects.all()

            patient_list = []
            for patient in patients:
                patient_list.append({
                    'patient_id': str(patient.id),
                    'firstname': patient.firstname,
                    'lastname': patient.lastname,
                    'email': patient.user.email if patient.user else None,
                    'phone': patient.phone,
                    'age': patient.age,
                    'gender': patient.gender,
                    'profile_image': patient.profile_image,
                })

            return JsonResponse({'patients': patient_list}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET method is allowed'}, status=405)

@csrf_exempt
def get_patient_by_id(request, patient_id):
    if request.method == 'GET':
        try:
            if not ObjectId.is_valid(patient_id):
                return JsonResponse({'error': 'Invalid patient ID'}, status=400)

            patient = Patient.objects(id=patient_id).first()
            if not patient:
                return JsonResponse({'error': 'Patient not found'}, status=404)

            return JsonResponse({
                'patient_id': str(patient.id),
                'firstname': patient.firstname,
                'lastname': patient.lastname,
                'email': patient.user.email if patient.user else None,
                'phone': patient.phone,
                'age': patient.age,
                'gender': patient.gender,
                'profile_image': patient.profile_image,
                'notes': getattr(patient, 'notes', ''),
                'national_id': patient.national_id,
                'hospital': str(patient.hospital.id) if patient.hospital else None
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET method is allowed'}, status=405)


@csrf_exempt
def delete_patient_by_id(request, patient_id):
    if request.method == 'DELETE':
        try:
            if not ObjectId.is_valid(patient_id):
                return JsonResponse({'error': 'Invalid patient ID'}, status=400)

            patient = Patient.objects(id=patient_id).first()
            if not patient:
                return JsonResponse({'error': 'Patient not found'}, status=404)

            # Optionally delete linked user too
            if patient.user:
                patient.user.delete()

            patient.delete()

            return JsonResponse({'message': 'Patient deleted successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only DELETE method is allowed'}, status=405)




@csrf_exempt
def update_patient_by_id(request, patient_id):
    if request.method == 'PUT':
        try:
            if not ObjectId.is_valid(patient_id):
                return JsonResponse({'error': 'Invalid patient ID'}, status=400)

            patient = Patient.objects(id=patient_id).first()
            if not patient:
                return JsonResponse({'error': 'Patient not found'}, status=404)

            data = json.loads(request.body.decode('utf-8'))

            # Update Patient fields if present in data
            fields_to_update = [
                'firstname', 'lastname', 'age', 'gender',
                'phone', 'height_cm', 'weight_kg', 'national_id', 'notes'
            ]
            for field in fields_to_update:
                if field in data:
                    setattr(patient, field, data[field])

            # Update hospital if hospital_id provided
            hospital_id = data.get('hospital_id')
            if hospital_id:
                if not ObjectId.is_valid(hospital_id):
                    return JsonResponse({'error': 'Invalid hospital ID'}, status=400)
                hospital = Hospital.objects(id=hospital_id).first()
                if not hospital:
                    return JsonResponse({'error': 'Hospital not found'}, status=404)
                patient.hospital = hospital

            patient.save()

            # Optionally update User email
            new_email = data.get('email')
            if new_email and patient.user:
                patient.user.email = new_email.lower().strip()
                patient.user.save()

            return JsonResponse({'message': 'Patient updated successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only PUT method is allowed'}, status=405)




