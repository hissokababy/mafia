import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TelegramLoginAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("status", models.CharField(choices=[("pending", "Ожидает подтверждения"), ("authenticated", "Подтверждён")], default="pending", max_length=20)),
                ("telegram_id", models.BigIntegerField(blank=True, null=True)),
                ("telegram_username", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="telegram_login_attempts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
