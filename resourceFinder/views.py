from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .medical_ai.ai_prediction import predict_diagnosis
from resourceFinder.medical_ai.models import PredictionTable
from resourceFinder.medical_ai.userModel import User  # Import user model
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult  # Import PredictionResult model

@csrf_exempt
def patient_predict(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            symptoms = data.get("symptoms", [])
            location = data.get("location")

            if not user_id or not symptoms or not location:
                return JsonResponse({"error": "User ID, symptoms, and location are required"}, status=400)

            # Find user
            user = User.objects(id=user_id).first()
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            # Get AI-based diagnosis and prediction
            result = predict_diagnosis(user, symptoms, location)

            # Save to PredictionResult model
            PredictionResult(
                user=user,
                symptoms=symptoms,
                location=location,
                diagnosis=result.get("diagnosis", ""),
                recommended_doctors=result.get("recommended_doctors", []),
                medical_supplies=result.get("medical_supplies", []),
                medical_resources=result.get("medical_resources", []),
                recommended_hospitals=result.get("recommended_hospitals", [])
            ).save()

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
