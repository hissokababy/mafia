from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True
    )
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    telegram_is_verified = models.BooleanField(default=False)

    nickname = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname or self.username


class TelegramLoginAttempt(models.Model):
    STATUS_CHOICES = (
        ("pending", "Ожидает подтверждения"),
        ("authenticated", "Подтверждён"),
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    telegram_id = models.BigIntegerField(null=True, blank=True)
    telegram_username = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="telegram_login_attempts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at
