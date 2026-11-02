from django.urls import path
from .views import (
    TelegramLoginStartView,
    TelegramLoginStatusView,
    TelegramBotConfirmView,
    TokenRefreshView,
    LogoutView,
    MeView,
)

urlpatterns = [
    path("auth/telegram/start/", TelegramLoginStartView.as_view(), name="telegram-login-start"),
    path("auth/telegram/status/", TelegramLoginStatusView.as_view(), name="telegram-login-status"),
    path("auth/telegram/confirm/", TelegramBotConfirmView.as_view(), name="telegram-login-confirm"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("users/me/", MeView.as_view(), name="user-me"),
]
