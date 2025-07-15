# utils/jwt_utils.py

from datetime import datetime, timedelta
import jwt
from django.conf import settings

def generate_jwt_token(user, extra_claims=None, lifetime_minutes=500):
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "userRole": user.userRole,
        "exp": datetime.utcnow() + timedelta(minutes=lifetime_minutes),
        "iat": datetime.utcnow(),
    }

    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token
