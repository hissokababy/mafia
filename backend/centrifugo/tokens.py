import time
import jwt

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def create_connection_token(user):
    if not settings.CENTRIFUGO_TOKEN_SECRET:
        raise ImproperlyConfigured(
            'CENTRIFUGO_TOKEN_SECRET не настроен'
        )

    payload = {
        'sub': str(user.id),
        'exp': int(time.time()) + 600,
    }

    token = jwt.encode(
        payload,
        settings.CENTRIFUGO_TOKEN_SECRET,
        algorithm='HS256',
    )

    return token


def create_subscription_token(user, room_id, channel_type='day'):
    if not settings.CENTRIFUGO_TOKEN_SECRET:
        raise ImproperlyConfigured(
            'CENTRIFUGO_TOKEN_SECRET не настроен'
        )

    channel = f'room:{room_id}:{channel_type}'

    payload = {
        'sub': str(user.id),
        'channel': channel,
        'exp': int(time.time()) + 600,
    }

    token = jwt.encode(
        payload,
        settings.CENTRIFUGO_TOKEN_SECRET,
        algorithm='HS256',
    )

    return token