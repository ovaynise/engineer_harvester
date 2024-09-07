from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import MAX_ROLE_LENGTH, CONFIRM_CODE_LENGTH


class MyUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]
    role = models.CharField(
        verbose_name='Права доступа',
        max_length=MAX_ROLE_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,

    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=CONFIRM_CODE_LENGTH,
        blank=True,

    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    bio = models.TextField(blank=True, null=True)
    patronymic = models.CharField(
        max_length=255,
        verbose_name='Отчество',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(
        verbose_name='Дата рождения',
        blank=True,
        null=True
    )
    phone_number = models.JSONField(default=list, null = True)

    class Meta:
        ordering = ['username']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Проверка на админа."""
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moder(self):
        """Проверка на модератора."""
        return self.role == self.MODERATOR


class TelegramUserModel(models.Model):
    user = models.OneToOneField(MyUser,
                                on_delete=models.CASCADE,
                                related_name='telegram_user',
                                null=True,
                                blank=True)
    level = models.BigIntegerField(default=15)
    tg_user_id = models.CharField(max_length=200, unique=True, null=False)
    tg_first_name = models.CharField(max_length=50, blank=True, null=True)
    tg_last_name = models.CharField(max_length=50, blank=True, null=True)
    tg_user_name = models.CharField(max_length=50, blank=True, null=True)
    ban_status = models.BooleanField(default=False)

    user_token = models.CharField(max_length=300, unique=True, null=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    def __str__(self):
        return self.nick_name


class BannedListModel(models.Model):
    banned_user = models.ForeignKey(TelegramUserModel,
                                    related_name='bans_as_user',
                                    on_delete=models.CASCADE)
    who_add_ban = models.ForeignKey(TelegramUserModel,
                                    related_name='bans_as_admin',
                                    on_delete=models.CASCADE)
    chat_nickname = models.CharField(max_length=200)
    ban_timer = models.BigIntegerField(default=None, blank=True, null=True)
    date_start_ban = models.DateTimeField()
    date_end_ban = models.DateTimeField(blank=True, null=True)
    ban_chat_id = models.CharField(max_length=200)
    ban_chat_status = models.CharField(max_length=200)
    warnings_count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    def __str__(self):
        return (f"Ban: {self.banned_user} by {self.who_add_ban} in "
                f"{self.chat_nickname}")
