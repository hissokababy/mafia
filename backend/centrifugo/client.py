import requests

from django.conf import settings


def publish(channel, data):
    """
    Отправляет событие в канал Centrifugo.
    """

    url = f'{settings.CENTRIFUGO_API_URL}/api/publish'

    headers = {
        'X-API-Key': settings.CENTRIFUGO_API_KEY,
    }

    payload = {
        'channel': channel,
        'data': data,
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=5,
    )

    response.raise_for_status()

    result = response.json()

    if 'error' in result:
        raise RuntimeError(result['error'])

    return result