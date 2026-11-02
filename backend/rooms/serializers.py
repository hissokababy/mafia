from rest_framework import serializers

from .models import Room, RoomPlayer


class RoomPlayerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = RoomPlayer
        fields = ['id', 'username', 'nickname', 'is_ready', 'joined_at']


class RoomSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True
    )
    players = RoomPlayerSerializer(many=True, read_only=True)
    players_count = serializers.IntegerField(
        source='players.count',
        read_only=True
    )

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'code',
            'owner',
            'owner_username',
            'max_players',
            'is_private',
            'status',
            'players',
            'players_count',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'code',
            'owner',
            'status',
            'created_at',
        ]

    def validate_max_players(self, value):
        if value < 4 or value > 20:
            raise serializers.ValidationError(
                'Количество игроков должно быть от 4 до 20.'
            )
        return value