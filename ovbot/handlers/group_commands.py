import asyncio
from datetime import datetime
from aiogram import Router, types, Bot
from modules.ai_integration import process_ai_response
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                UserLevelRangeFilter, security_filters, GroupChatInteractionFilter)

group_commands_router = Router()

# Общие фильтры для проверки типа чата и уровня доступа
common_filters = [
    ChatTypesFilter(["group", "supergroup"]),  # Обновлено
    UserLevelFilter(0, 15, "IsAuthUser"),
]

# Список запрещенных слов
FORBIDDEN_WORDS = ["жопа"]

def setup_group_commands_handlers(ovay_bot):
    # Фильтр для мониторинга сообщений и предупреждения за запрещенные слова
    @group_commands_router.message()
    async def monitor_messages(msg: types.Message):
        # Проверка на запрещенные слова
        if any(word in msg.text.lower() for word in FORBIDDEN_WORDS):
            await msg.reply(f"{msg.from_user.username}, пожалуйста, соблюдайте правила чата!")

    # Обработчик для команды времени
    @security_filters(group_commands_router, "time", *common_filters)
    async def show_time(message: types.Message):
        today = datetime.today()
        await message.answer(f"{today}")

    # Обработчик для ИИ-команд (только для reply или упоминания бота)
    @security_filters(
        group_commands_router,
        None,
        UserLevelRangeFilter(min_level=0, max_level=15),
        GroupChatInteractionFilter(ovay_bot),  # Проверка на упоминание или reply
        *common_filters,
    )
    async def ai_or_log_message(msg: types.Message):
        user_message = msg.text
        user_id = msg.from_user.id
        chat_id = msg.chat.id
        username = msg.from_user.username or "Без имени"
        chat_title = msg.chat.title if msg.chat.title else username

        # Обработка сообщения с ИИ
        bot_message = process_ai_response(user_id, chat_id, username, user_message)

        # Логирование и отправка ответа
        await ovay_bot.info_message(
            chat_id=chat_id,
            bot_message=bot_message,
            user_message=user_message,
            user_id=user_id,
            username=username,
            chat_title=chat_title
        )

    return group_commands_router