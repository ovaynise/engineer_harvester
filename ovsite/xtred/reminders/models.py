from django.db import models

from core.models import BaseModel


class Reminder(BaseModel):
    id = models.AutoField(primary_key=True)
    reminder_nickname = models.TextField(verbose_name='Ник владельца')
    name_reminder = models.TextField(verbose_name='Название напоминания')
    status_reminder = models.BooleanField(default=False)
    night_mode = models.BooleanField(default=False)
    text_reminder = models.TextField(max_length=2000)
    days_repeat = models.JSONField(null=True, blank=True)
    interval_repeat = models.JSONField(default=list)
    chats_id_active = models.JSONField(default=list)
    chats_names_active = models.JSONField(default=list)
    start_at = models.DateTimeField(null=True, blank=True)
    owner_reminder_id = models.TextField(verbose_name='ID владельца')
    reminder_chat_id = models.TextField(verbose_name='ID чата')
    reminder_last_view_time = models.DateTimeField(null=True, blank=True)
    next_reminder_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
