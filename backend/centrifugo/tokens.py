import time
import jwt

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.core.exceptions import PermissionDenied
from game.models import PlayerRole

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

    if not user.is_authenticated:
        raise PermissionDenied('Необходима авторизация')

    if channel_type not in ('day', 'night'):
        raise PermissionDenied('Неизвестный канал')

    # Ищем активную игровую роль пользователя
    player_role = PlayerRole.objects.filter(
        game__room_id=room_id,
        player=user,
        game__status__in=('day', 'night', 'voting'),
        is_alive=True,
    ).select_related('game').order_by('-game__created_at').first()

    if not player_role:
        raise PermissionDenied('Вы не участвуете в этой игре')

    game = player_role.game

    # Проверяем доступ к ночному каналу
    if channel_type == 'night':
        if game.status != 'night':
            raise PermissionDenied('Сейчас не ночная фаза')

        if player_role.role not in ('mafia', 'don'):
            raise PermissionDenied('У вас нет доступа к каналу мафии')

    # Проверяем доступ к дневному каналу
    if channel_type == 'day':
        if game.status not in ('day', 'voting'):
            raise PermissionDenied('Сейчас дневной канал недоступен')

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

    return jwt.encode(
        payload,
        settings.CENTRIFUGO_TOKEN_SECRET,
        algorithm='HS256',
    )