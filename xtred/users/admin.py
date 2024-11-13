from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser, TelegramUserModel

UserAdmin.fieldsets += (("Extra Fields", {"fields": ("bio",)}),)


class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('tg_user_id', 'tg_user_name', 'tg_first_name',
                    'tg_last_name', 'ban_status', 'level')
    search_fields = ('tg_user_name', 'tg_user_id')
    list_filter = ('ban_status', 'level')
    readonly_fields = ('created_at',)


admin.site.register(MyUser, UserAdmin)
admin.site.register(TelegramUserModel, TelegramUserAdmin)
