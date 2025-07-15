# resourceFinder/middleware/auth.py
from django.http import JsonResponse
import jwt
from dotenv import load_dotenv
load_dotenv()
import os
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", 'fallback-secret-key-if-missing')
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") 

def token_auth_middleware(get_response):
    def middleware(request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                decoded = jwt.decode(token, JWT_SECRET_KEY or SECRET_KEY, algorithms=["HS256"])
                request.user_id = decoded.get("user_id")
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token has expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token"}, status=401)
        else:
            request.user_id = None
        return get_response(request)
    return middleware