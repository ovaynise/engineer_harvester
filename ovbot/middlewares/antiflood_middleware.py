import logging
import time
from collections import defaultdict
from aiogram import BaseMiddleware, Bot
from middlewares.user_block_manager import is_user_blocked, block_user, add_user_warning, get_user_warnings
from aiogram.types import Message, Update, ChatPermissions

logger = logging.getLogger(__name__)
logger_other = logging.getLogger("logger_other")

# Константы антифлуда
MAX_MESSAGES = 2  # Максимальное количество сообщений
TIME_WINDOW = 2  # Время в секундах для проверки частоты сообщений
BAN_DURATION_GROUP = 300  # Блокировка в группах в секундах (5 минут)

# Кэш для хранения времени сообщений
user_message_times = defaultdict(list)


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    async def __call__(self, handler, event: Update, data: dict):
        if not isinstance(event, Update) or not event.message or not isinstance(event.message, Message):
            return await handler(event, data)

        message = event.message
        user_id = message.from_user.id
        chat_id = message.chat.id
        current_time = time.time()

        # Пропускаем обработку для личных сообщений
        if message.chat.type == "private":
            return await handler(event, data)

        logger_other.info(f"Антифлуд: Проверяем сообщение от пользователя {user_id} в группе {chat_id}.")
        logger_other.debug(f"Текст сообщения: {message.text}")

        # Удаляем старые записи из кэша
        old_count = len(user_message_times[user_id])
        user_message_times[user_id] = [
            t for t in user_message_times[user_id] if current_time - t < TIME_WINDOW
        ]
        logger_other.debug(f"Удалено {old_count - len(user_message_times[user_id])} старых записей из кэша для пользователя {user_id}.")

        # Добавляем текущее время в кэше
        user_message_times[user_id].append(current_time)
        logger_other.debug(f"Обновлён кэш для пользователя {user_id}: {user_message_times[user_id]}.")

        # Проверяем наличие блокировки
        if is_user_blocked(chat_id, user_id):
            logger_other.info(f"Антифлуд: Пользователь {user_id} уже заблокирован.")
            return  # Игнорируем сообщения

        # Проверяем лимит сообщений
        if len(user_message_times[user_id]) > MAX_MESSAGES:
            logger_other.info(f"Антифлуд: Пользователь {user_id} превысил лимит сообщений в чате {chat_id}.")
            add_user_warning(chat_id, user_id)
            warnings = get_user_warnings(chat_id, user_id)
            logger_other.warning(f"Антифлуд: Пользователь {user_id} получил предупреждение ({warnings}/3).")

            if warnings >= 3:
                logger_other.info(f"Антифлуд: Блокируем пользователя {user_id} в чате {chat_id}.")
                block_user(chat_id, user_id, duration=BAN_DURATION_GROUP, reason="flood")
                try:
                    await self.bot.restrict_chat_member(
                        chat_id,
                        user_id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=int(current_time) + BAN_DURATION_GROUP
                    )
                    await message.reply(
                        f"{message.from_user.username} заблокирован за флуд на {BAN_DURATION_GROUP // 60} минут."
                    )
                    logger_other.info(f"Антифлуд: Пользователь {user_id} успешно заблокирован в группе {chat_id}.")
                except Exception as e:
                    logger_other.error(f"Ошибка при блокировке пользователя {user_id} в группе {chat_id}: {e}")
                return

            # Отправляем предупреждение
            await message.reply(
                f"{message.from_user.username}, это предупреждение за флуд. Осталось {3 - warnings}."
            )
            logger_other.info(f"Антифлуд: Предупреждение отправлено пользователю {user_id} в группе {chat_id}.")
            return

        # Если лимит не превышен, передаём управление дальше
        return await handler(event, data)