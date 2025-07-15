import random
import uuid
from django.http import JsonResponse
from resourceFinder.medical_ai.userModel import User
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from resourceFinder.utility.email_sender import send_email

from django.contrib.auth.hashers import make_password
import json

@csrf_exempt
def request_password_reset(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid or empty JSON body"}, status=400)

    email = data.get("email")
    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    user = User.objects(email=email).first()
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    # Generate a 6-digit numeric OTP
    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=30)

    user.reset_password_otp = otp
    user.reset_password_expiry = expiry
    user.save()

    send_email(
        email,
        "Your Password Reset OTP",
        f"Your OTP to reset the password is: {otp}. It will expire in 30 minutes."
    )

    return JsonResponse({"message": "OTP sent to your email."}, status=200)

@csrf_exempt
def reset_password_with_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid or empty JSON body"}, status=400)

    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    if not all([email, otp, new_password]):
        return JsonResponse({"error": "Email, OTP, and new password are required"}, status=400)

    user = User.objects(email=email).first()
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    if user.reset_password_otp != otp:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    if not user.reset_password_expiry or datetime.utcnow() > user.reset_password_expiry:
        return JsonResponse({"error": "OTP expired"}, status=400)

    user.password = make_password(new_password)
    user.reset_password_otp = None
    user.reset_password_expiry = None
    user.save()

    return JsonResponse({"message": "Password has been reset successfully."}, status=200)