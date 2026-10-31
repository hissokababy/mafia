from django.contrib import admin
from .models import Room, RoomInvitation, RoomPlayer


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'code',
        'owner',
        'max_players',
        'is_private',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'is_private',
        'created_at',
    )

    search_fields = (
        'name',
        'owner__username',
        'owner__nickname',
    )

@admin.register(RoomPlayer)
class RoomPlayerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'room',
        'user',
        'is_ready',
        'is_alive',
        'joined_at',
    )

    list_filter = (
        'is_ready',
        'is_alive',
    )

    search_fields = (
        'room__name',
        'user__username',
        'user__nickname',
    )


@admin.register(RoomInvitation)
class RoomInvitationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'room',
        'sender',
        'receiver',
        'status',
        'created_at',
        'expires_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'sender__nickname',
        'receiver__nickname',
        'room__name',
    )

