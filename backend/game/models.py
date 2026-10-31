from django.db import models
from django.conf import settings
from rooms.models import Room


class GameSession(models.Model):

    STATUS_CHOICES = (
        ('waiting', 'Ожидание'),
        ('night', 'Ночь'),
        ('day', 'День'),
        ('voting', 'Голосование'),
        ('finished', 'Завершена'),
    )

    WINNER_CHOICES = (
        ('mafia', 'Мафия'),
        ('town', 'Мирные жители'),
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='games',
        verbose_name='Комната'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='waiting',
        verbose_name='Статус игры'
    )

    round_number = models.PositiveIntegerField(
        default=0,
        verbose_name='Номер раунда'
    )

    winner = models.CharField(
        max_length=10,
        choices=WINNER_CHOICES,
        blank=True,
        verbose_name='Победитель'
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Игровая партия'
        verbose_name_plural = 'Игровые партии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Игра #{self.id} — {self.room.name}'


class PlayerRole(models.Model):

    ROLE_CHOICES = (
        ('mafia', 'Мафия'),
        ('don', 'Дон мафии'),
        ('doctor', 'Доктор'),
        ('detective', 'Комиссар'),
        ('civilian', 'Мирный житель'),
    )

    game = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='player_roles',
        verbose_name='Игра'
    )

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_roles',
        verbose_name='Игрок'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Роль'
    )

    is_alive = models.BooleanField(
        default=True,
        verbose_name='Жив'
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата назначения роли'
    )

    class Meta:
        verbose_name = 'Роль игрока'
        verbose_name_plural = 'Роли игроков'

        constraints = [
            models.UniqueConstraint(
                fields=['game', 'player'],
                name='unique_player_role_per_game'
            )
        ]

    def __str__(self):
        return f'{self.player} — {self.get_role_display()}'


class GameAction(models.Model):

    ACTION_CHOICES = (
        ('kill', 'Убийство'),
        ('heal', 'Лечение'),
        ('investigate', 'Проверка'),
        ('vote', 'Голосование'),
    )

    game = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name='Игра'
    )

    actor = models.ForeignKey(
        PlayerRole,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name='Кто совершил действие'
    )

    target = models.ForeignKey(
        PlayerRole,
        on_delete=models.CASCADE,
        related_name='targeted_actions',
        null=True,
        blank=True,
        verbose_name='Цель действия'
    )

    action_type = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Тип действия'
    )

    round_number = models.PositiveIntegerField(
        verbose_name='Номер раунда'
    )

    is_resolved = models.BooleanField(
        default=False,
        verbose_name='Обработано'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время действия'
    )

    class Meta:
        verbose_name = 'Игровое действие'
        verbose_name_plural = 'Игровые действия'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.actor} — {self.get_action_type_display()}'