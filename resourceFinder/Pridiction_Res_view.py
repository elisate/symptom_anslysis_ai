from django.http import JsonResponse
from resourceFinder.medical_ai.PredictionResult_model import PredictionResult
from resourceFinder.medical_ai.userModel import User

from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from django.views.decorators.http import require_GET
def get_prediction_result(request):
    if request.method == "GET":
        try:
            # Middleware must have added this
            user_id = getattr(request, "user_id", None)

            if not user_id:
                return JsonResponse({"error": "Unauthorized. No user ID found in request."}, status=401)

            # Find user by ID
            user = User.objects(id=user_id).first()
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            # Fetch latest prediction for the user
            prediction = PredictionResult.objects(user=user).order_by("-created_at").first()

            if prediction:
                # Convert prediction to dict, then inject the prediction ID
                prediction_data = prediction.to_dict() if hasattr(prediction, "to_dict") else prediction.to_mongo().to_dict()
                prediction_data["prediction_id"] = str(prediction.id)  # Add the ID as 'prediction_id'
                
                return JsonResponse(prediction_data, status=200)
            else:
                return JsonResponse({"error": "No prediction found for this user"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method. Only GET allowed."}, status=405)


def get_prediction_by_id(request, prediction_id):
    if request.method == "GET":
        try:
            # Look up the prediction by ID
            prediction = PredictionResult.objects(id=prediction_id).first()

            if not prediction:
                return JsonResponse({"error": "Prediction not found"}, status=404)

            # Convert to dict and include the ID
            prediction_data = prediction.to_dict() if hasattr(prediction, "to_dict") else prediction.to_mongo().to_dict()
            prediction_data["prediction_id"] = str(prediction.id)

            return JsonResponse(prediction_data, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method. Only GET allowed."}, status=405)


@csrf_exempt
def get_all_predictions(request):
    if request.method == "GET":
        try:
            predictions = PredictionResult.objects().order_by("-created_at")

            prediction_list = []
            for prediction in predictions:
                data = prediction.to_mongo().to_dict()
                data["_id"] = str(data["_id"])  # ✅ Convert ObjectId to string
                data["user"] = str(data["user"]) if "user" in data else None  # if you include user field
                prediction_list.append(data)

            return JsonResponse({"predictions": prediction_list}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method. Only GET allowed."}, status=405)


@require_GET
def get_predictions_by_user_id(request, user_id):
    try:
        # Validate and find user
        user = User.objects(id=ObjectId(user_id)).first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        # Fetch all predictions for this user
        predictions = PredictionResult.objects(user=user).order_by("-created_at")

        prediction_list = []
        for prediction in predictions:
            data = prediction.to_mongo().to_dict()
            data["_id"] = str(data["_id"])  # convert ObjectId to string
            data["user"] = str(data["user"]) if "user" in data else None
            prediction_list.append(data)

        return JsonResponse({"predictions": prediction_list}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)