import hmac
import secrets
from datetime import timedelta
from uuid import UUID

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelegramLoginAttempt
from .serializers import UserProfileSerializer


def _make_token(user, token_type, lifetime):
    now = timezone.now()
    payload = {
        "sub": str(user.pk),
        "typ": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + lifetime).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def _set_refresh_cookie(response, user):
    refresh = _make_token(user, "refresh", timedelta(days=30))
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        refresh,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path="/api/v1/auth/",
    )


class TelegramLoginStartView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        bot_username = getattr(settings, "TELEGRAM_BOT_USERNAME", "").lstrip("@")
        if not bot_username:
            return Response(
                {"detail": "TELEGRAM_BOT_USERNAME is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        attempt = TelegramLoginAttempt.objects.create(
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        deep_link = f"https://t.me/{bot_username}?start=login_{attempt.token}"
        return Response({
            "attempt_id": str(attempt.token),
            "bot_url": deep_link,
            "expires_in": 300,
            "poll_interval": 2,
        }, status=status.HTTP_201_CREATED)


class TelegramLoginStatusView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        raw_token = request.query_params.get("attempt_id", "")
        try:
            token = UUID(raw_token)
        except (ValueError, TypeError, AttributeError):
            return Response({"detail": "Invalid attempt_id."}, status=400)

        try:
            attempt = TelegramLoginAttempt.objects.select_related("user").get(token=token)
        except TelegramLoginAttempt.DoesNotExist:
            return Response({"detail": "Login attempt not found."}, status=404)

        if attempt.is_expired:
            return Response({"status": "expired"}, status=410)

        if attempt.status != "authenticated" or not attempt.user:
            return Response({"status": "pending"})

        access = _make_token(attempt.user, "access", timedelta(minutes=10))
        response = Response({
            "status": "authenticated",
            "access": access,
            "user": UserProfileSerializer(attempt.user).data,
        })
        _set_refresh_cookie(response, attempt.user)
        return response


class TelegramBotConfirmView(APIView):
    """Private endpoint called only by our trusted Telegram bot backend."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        configured_secret = getattr(settings, "TELEGRAM_BOT_WEBHOOK_SECRET", "")
        supplied_secret = request.headers.get("X-Bot-Secret", "")
        if not configured_secret or not hmac.compare_digest(
            str(supplied_secret), str(configured_secret)
        ):
            return Response({"detail": "Forbidden."}, status=403)

        raw_token = request.data.get("token", "")
        telegram_id = request.data.get("telegram_id")
        telegram_username = (request.data.get("telegram_username") or "")[:100]

        try:
            token = UUID(str(raw_token))
            telegram_id = int(telegram_id)
            if telegram_id <= 0:
                raise ValueError
        except (ValueError, TypeError, AttributeError):
            return Response({"detail": "Invalid token or telegram_id."}, status=400)

        try:
            attempt = TelegramLoginAttempt.objects.get(token=token)
        except TelegramLoginAttempt.DoesNotExist:
            return Response({"detail": "Login attempt not found."}, status=404)

        if attempt.is_expired:
            return Response({"detail": "Login attempt expired."}, status=410)

        if attempt.status == "authenticated":
            if attempt.telegram_id == telegram_id:
                return Response({"status": "authenticated"})
            return Response({"detail": "Attempt already used."}, status=409)

        User = get_user_model()
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": f"tg_{telegram_id}",
                "telegram_username": telegram_username,
                "telegram_is_verified": True,
                "nickname": telegram_username or f"Player{str(telegram_id)[-5:]}",
            },
        )

        changed_fields = []
        if not user.telegram_is_verified:
            user.telegram_is_verified = True
            changed_fields.append("telegram_is_verified")
        if telegram_username and user.telegram_username != telegram_username:
            user.telegram_username = telegram_username
            changed_fields.append("telegram_username")
        if not user.nickname and telegram_username:
            user.nickname = telegram_username
            changed_fields.append("nickname")
        if created:
            user.set_unusable_password()
            changed_fields.extend(["password"])
        if changed_fields:
            user.save(update_fields=list(set(changed_fields)))

        attempt.telegram_id = telegram_id
        attempt.telegram_username = telegram_username
        attempt.user = user
        attempt.status = "authenticated"
        attempt.confirmed_at = timezone.now()
        attempt.save(update_fields=[
            "telegram_id", "telegram_username", "user", "status", "confirmed_at"
        ])
        return Response({"status": "authenticated"})


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        raw_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        if not raw_token:
            return Response({"detail": "Refresh token missing."}, status=401)

        try:
            payload = jwt.decode(
                raw_token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"require": ["sub", "exp", "typ"]},
            )
            if payload.get("typ") != "refresh":
                raise jwt.InvalidTokenError("Wrong token type.")
            user = get_user_model().objects.get(pk=payload["sub"], is_active=True)
        except (jwt.PyJWTError, get_user_model().DoesNotExist, ValueError) as exc:
            response = Response({"detail": "Invalid refresh token."}, status=401)
            response.delete_cookie(settings.AUTH_REFRESH_COOKIE_NAME, path="/api/v1/auth/")
            return response

        response = Response({
            "access": _make_token(user, "access", timedelta(minutes=10))
        })
        _set_refresh_cookie(response, user)
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        response = Response({"detail": "Logged out."})
        response.delete_cookie(settings.AUTH_REFRESH_COOKIE_NAME, path="/api/v1/auth/")
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        nickname = request.data.get("nickname")
        if nickname is not None:
            nickname = str(nickname).strip()
            if not nickname or len(nickname) > 30:
                return Response({"nickname": "Nickname must contain 1–30 characters."}, status=400)
            request.user.nickname = nickname
            request.user.save(update_fields=["nickname"])
        return Response(UserProfileSerializer(request.user).data)
