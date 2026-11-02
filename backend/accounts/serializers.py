from rest_framework import serializers


class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    telegram_id = serializers.IntegerField(read_only=True)
    telegram_username = serializers.CharField(read_only=True)
    nickname = serializers.CharField(max_length=30, required=False, allow_blank=True)
    avatar = serializers.ImageField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
