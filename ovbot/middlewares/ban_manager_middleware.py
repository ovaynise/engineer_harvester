import logging
import time
from aiogram import BaseMiddleware, Bot
from aiogram.types import Update, ChatPermissions
from middlewares.user_block_manager import (
    is_user_blocked,
    get_user_warnings,
    reset_warnings,
    add_user_warning
)  # Импортируем необходимые функции
from config import logger_other
from middlewares.user_block_manager import blocked_users, block_user

# Константы длительности блокировки
FIRST_BLOCK_DURATION = 60  # 1 минута
SECOND_BLOCK_DURATION = 180  # 3 минуты
THIRD_BLOCK_DURATION = 300  # 5 минут

# Кэш для хранения пользователей, которым отправлено сообщение
notified_admins = set()

async def restrict_user(bot, chat_id, user_id, warnings_count, reset_warnings_callback):
    """Ограничивает пользователя в чате на основе количества предупреждений."""
    try:
        # Проверяем тип чата
        chat_type = await bot.get_chat(chat_id)
        is_private = chat_type.type == "private"

        # Определяем длительность блокировки на основе количества предупреждений
        duration_seconds = [FIRST_BLOCK_DURATION, SECOND_BLOCK_DURATION, THIRD_BLOCK_DURATION][min(warnings_count - 1, 2)]
        until_date = int(time.time()) + duration_seconds

        if is_private:
            # Если чат личный, отправляем сообщение о блокировке
            await bot.send_message(
                chat_id,
                f"Вы заблокированы за нарушение правил. Вы не сможете отправлять сообщения до "
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(until_date))}."
            )
            block_user(chat_id, user_id, duration=duration_seconds, reason="bad_words")
            logger_other.info(f"Пользователь {user_id} заблокирован в личном чате до {until_date}.")
            return
        else:
            # Если чат групповой, применяем ограничение
            await bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            await bot.send_message(
                chat_id,
                f"Пользователь {user_id} заблокирован на {duration_seconds // 60} минут(ы)."
            )
            block_user(chat_id, user_id, duration=duration_seconds, reason="bad_words")
            logger_other.info(f"Пользователь {user_id} успешно заблокирован в чате {chat_id} на {duration_seconds} секунд.")

    except Exception as e:
        logger_other.error(f"Ошибка при блокировке пользователя {user_id} в чате {chat_id}: {e}")


class BanManagerMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    async def __call__(self, handler, event: Update, data: dict):
        if event.message:
            message = event.message
            user_id = message.from_user.id
            chat_id = message.chat.id

            # Проверяем, заблокирован ли пользователь
            if is_user_blocked(chat_id, user_id):
                logger_other.info(f"BanManager: Пользователь {user_id} уже заблокирован. Ограничиваем доступ.")
                try:
                    await self.bot.restrict_chat_member(
                        chat_id,
                        user_id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=int(time.time()) + 300
                    )
                except Exception as e:
                    logger_other.error(f"Ошибка ограничения пользователя {user_id}: {e}")
                return

        return await handler(event, data)