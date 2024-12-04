import logging
import time
from collections import defaultdict
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, Update

logger = logging.getLogger(__name__)

# Константы антифлуда для личных сообщений
MAX_MESSAGES_PRIVATE = 2  # Максимальное количество сообщений
TIME_WINDOW_PRIVATE = 2  # Время в секундах для проверки частоты сообщений
BAN_DURATION_PRIVATE = 300  # Время блокировки в личных сообщениях (5 минут)

# Кэш для хранения времени сообщений в личных чатах
private_message_times = defaultdict(list)
# Кэш для хранения времени блокировки пользователей
private_blocked_users = {}


class PrivateFloodMiddleware(BaseMiddleware):
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

        # Обрабатываем только личные сообщения
        if message.chat.type != "private":
            logger.debug(f"Антифлуд (личные сообщения): Сообщение от {user_id} не из личного чата, пропускаем.")
            return await handler(event, data)

        logger.info(f"Антифлуд (личные сообщения): Проверяем сообщение от пользователя {user_id}.")

        # Если пользователь в блокировке
        if user_id in private_blocked_users and current_time < private_blocked_users[user_id]:
            block_end_time = private_blocked_users[user_id]
            logger.info(f"Антифлуд (личные сообщения): Пользователь {user_id} заблокирован до "
                        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block_end_time))}.")
            return  # Игнорируем сообщение

        # Очищаем старые записи
        old_count = len(private_message_times[user_id])
        private_message_times[user_id] = [
            t for t in private_message_times[user_id] if current_time - t < TIME_WINDOW_PRIVATE
        ]
        logger.debug(f"Антифлуд (личные сообщения): Удалено {old_count - len(private_message_times[user_id])} "
                     f"старых записей для пользователя {user_id}.")

        # Добавляем текущее время сообщения
        private_message_times[user_id].append(current_time)
        logger.debug(f"Антифлуд (личные сообщения): Обновлён кэш сообщений для пользователя {user_id}: "
                     f"{private_message_times[user_id]}.")

        # Проверяем лимит сообщений
        if len(private_message_times[user_id]) > MAX_MESSAGES_PRIVATE:
            block_end_time = current_time + BAN_DURATION_PRIVATE
            private_blocked_users[user_id] = block_end_time
            logger.warning(f"Антифлуд (личные сообщения): Пользователь {user_id} превысил лимит сообщений и заблокирован.")

            try:
                await self.bot.send_message(
                    chat_id,
                    f"Вы были заблокированы за флуд. Вы сможете отправлять сообщения после "
                    f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block_end_time))}."
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления о блокировке: {e}")

            return  # Прерываем обработку сообщения

        logger.debug(f"Антифлуд (личные сообщения): Пользователь {user_id} не превысил лимит, передаём управление.")
        # Если пользователь не превышал лимит, передаём управление дальше
        return await handler(event, data)