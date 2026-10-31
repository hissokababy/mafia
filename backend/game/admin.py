from django.contrib import admin
from .models import GameAction, GameSession, PlayerRole


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'room',
        'status',
        'round_number',
        'winner',
        'created_at',
    )

    list_filter = (
        'status',
        'winner',
    )

    search_fields = (
        'room__name',
    )


@admin.register(PlayerRole)
class PlayerRoleAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'game',
        'player',
        'role',
        'is_alive',
        'assigned_at',
    )

    list_filter = (
        'role',
        'is_alive',
    )

    search_fields = (
        'player__nickname',
        'player__username',
    )


@admin.register(GameAction)
class GameActionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'game',
        'actor',
        'target',
        'action_type',
        'round_number',
        'is_resolved',
        'created_at',
    )

    list_filter = (
        'action_type',
        'is_resolved',
        'round_number',
    )

    search_fields = (
        'actor__player__username',
        'target__player__username',
    )