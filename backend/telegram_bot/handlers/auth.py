import os
import requests

from telebot import TeleBot


DJANGO_API_URL = os.getenv(
    "DJANGO_API_URL",
    "http://127.0.0.1:8000"
)

TELEGRAM_BOT_WEBHOOK_SECRET = os.getenv(
    "TELEGRAM_BOT_WEBHOOK_SECRET"
)


def handle_telegram_login(bot: TeleBot, message):
    """
    Обрабатывает deep link:
    /start login_TOKEN
    """

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        return False

    payload = args[1].strip()

    if not payload.startswith("login_"):
        return False

    token = payload.removeprefix("login_")

    if not token:
        bot.send_message(
            message.chat.id,
            "Некорректная ссылка авторизации."
        )
        return True

    telegram_id = message.from_user.id
    telegram_username = message.from_user.username

    try:
        response = requests.post(
            f"{DJANGO_API_URL}/api/v1/auth/telegram/confirm/",
            json={
                "token": token,
                "telegram_id": telegram_id,
                "telegram_username": telegram_username,
            },
            headers={
                "X-Bot-Secret": TELEGRAM_BOT_WEBHOOK_SECRET
            },
            timeout=10
        )

        response.raise_for_status()

        bot.send_message(
            message.chat.id,
            "✅ Авторизация подтверждена!\n\n"
            "Вернитесь на сайт Mafia."
        )

    except requests.RequestException:
        bot.send_message(
            message.chat.id,
            "❌ Не удалось подтвердить авторизацию. "
            "Попробуйте ещё раз."
        )

    return True