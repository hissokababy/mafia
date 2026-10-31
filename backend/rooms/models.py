import uuid

from django.conf import settings
from django.db import models


class Room(models.Model):

    STATUS_CHOICES = (
        ('waiting', 'Ожидание игроков'),
        ('playing', 'Игра идёт'),
        ('finished', 'Игра завершена'),
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Название комнаты'
    )

    code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='Код комнаты'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_rooms',
        verbose_name='Создатель'
    )

    max_players = models.PositiveSmallIntegerField(
        default=10,
        verbose_name='Максимум игроков'
    )

    is_private = models.BooleanField(
        default=True,
        verbose_name='Приватная комната'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='waiting',
        verbose_name='Статус'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f'{self.name} ({self.code})'

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
        ordering = ['-created_at']


class RoomPlayer(models.Model):

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='players',
        verbose_name='Комната'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='room_memberships',
        verbose_name='Игрок'
    )

    is_ready = models.BooleanField(
        default=False,
        verbose_name='Готов к игре'
    )

    is_alive = models.BooleanField(
        default=True,
        verbose_name='Жив'
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подключения'
    )

    class Meta:
        verbose_name = 'Участник комнаты'
        verbose_name_plural = 'Участники комнат'

        constraints = [
            models.UniqueConstraint(
                fields=['room', 'user'],
                name='unique_room_player'
            )
        ]

    def __str__(self):
        return f'{self.user} — {self.room.name}'


class RoomInvitation(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Ожидает ответа'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
        ('expired', 'Истекло'),
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='Комната'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_room_invitations',
        verbose_name='Отправитель'
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_room_invitations',
        verbose_name='Получатель'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отправки'
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Срок действия'
    )

    class Meta:
        verbose_name = 'Приглашение в комнату'
        verbose_name_plural = 'Приглашения в комнаты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender} → {self.receiver} ({self.room.name})'