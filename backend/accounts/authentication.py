import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTAuthentication(BaseAuthentication):
    """Authenticate API calls with a short-lived Bearer access token."""

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Invalid authorization header.")

        try:
            payload = jwt.decode(
                parts[1],
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"require": ["sub", "exp", "typ"]},
            )
        except jwt.PyJWTError as exc:
            raise AuthenticationFailed("Invalid or expired access token.") from exc

        if payload.get("typ") != "access":
            raise AuthenticationFailed("Invalid token type.")

        User = get_user_model()
        try:
            user = User.objects.get(pk=payload["sub"], is_active=True)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User not found.") from exc

        return user, parts[1]
