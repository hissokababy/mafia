from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .tokens import (
    create_connection_token,
    create_subscription_token,
)


class CentrifugoTokenView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        room_id = request.data.get('room_id')
        channel_type = request.data.get('channel_type', 'day')

        if not room_id:
            return Response(
                {'error': 'Не указан room_id'},
                status=400
            )

        try:
            subscription_token = create_subscription_token(
                request.user,
                room_id,
                channel_type
            )

        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))

        connection_token = create_connection_token(request.user)

        return Response({
            'connection_token': connection_token,
            'subscription_token': subscription_token,
            'channel': f'room:{room_id}:{channel_type}',
        })