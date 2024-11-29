import time
from middlewares.blocked_users import blocked_users
from datetime import datetime
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, Update, ChatPermissions
from collections import defaultdict
from config import TELEGRAM_GROUP_ID, logger_other


INITIAL_BLOCK_DURATION = 1
SECOND_BLOCK_DURATION = 5
SUBSEQUENT_BLOCK_DURATION = 30


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, rate_limit: int = 2, warning_limit: int = 2):
        super().__init__()
        self.bot = bot
        self.rate_limit = rate_limit
        self.warning_limit = warning_limit

    async def __call__(self, handler, event: Update, data: dict):
        if isinstance(event, Update) and event.message and isinstance(event.message, Message):
            message = event.message
            user_id = message.from_user.id
            chat_id = message.chat.id
            current_time = time.time()

            # Проверка на блокировку пользователя (если уже заблокирован, игнорируем его)
            if chat_id in blocked_users and user_id in blocked_users[chat_id]:
                block_end_time = blocked_users[chat_id][user_id]["blocked_until"]
                if block_end_time > current_time:
                    if message.chat.type == "private" and not blocked_users[chat_id][user_id].get("block_notified", False):
                        readable_block_end = datetime.fromtimestamp(block_end_time).strftime('%Y-%m-%d %H:%M:%S')
                        await message.reply(f"Вы заблокированы до {readable_block_end}.")
                        blocked_users[chat_id][user_id]["block_notified"] = True
                    return  # Игнорируем сообщения, пока не пройдет блокировка

            # Логика антифлуд фильтра
            last_activity = blocked_users[chat_id].get(user_id, {"time": 0, "warnings": 0})
            if current_time - last_activity["time"] < self.rate_limit:
                last_activity["warnings"] += 1
                if last_activity["warnings"] >= self.warning_limit:
                    block_duration = INITIAL_BLOCK_DURATION * 60
                    block_end_time = current_time + block_duration
                    readable_block_end = datetime.fromtimestamp(block_end_time).strftime('%Y-%m-%d %H:%M:%S')

                    try:
                        await self.bot.restrict_chat_member(
                            chat_id, user_id,
                            permissions=ChatPermissions(can_send_messages=False),
                            until_date=block_end_time
                        )
                    except Exception as e:
                        logger_other.error(f"Не удалось заблокировать пользователя {user_id} в чате {chat_id}: {e}")

                    # Обновляем блокировку в чате
                    if chat_id not in blocked_users:
                        blocked_users[chat_id] = {}

                    blocked_users[chat_id][user_id] = {
                        "blocked_until": block_end_time,
                        "reason": "spam",
                        "block_notified": False
                    }

                    # Отправляем сообщение в группу
                    await self.bot.send_message(
                        TELEGRAM_GROUP_ID,
                        f"Пользователь @{message.from_user.username} заблокирован за спам.\n"
                        f"Чат: {message.chat.title if message.chat.title else 'Без названия'}\n"
                        f"Причина: Спам сообщений.\n"
                        f"Заблокирован до: {readable_block_end}"
                    )

                    # Отправляем сообщение в личку
                    if message.chat.type == "private":
                        await message.reply(f"Вы были заблокированы до {readable_block_end} за спам.")

                    return  # Больше не реагируем на пользователя

                blocked_users[chat_id][user_id] = last_activity
                remaining_warnings = self.warning_limit - last_activity["warnings"]
                await message.reply(f"{message.from_user.username}, ваше сообщение слишком частое. У вас осталось {remaining_warnings} предупреждений.")
                return

            # Сбрасываем предупреждения, если прошло достаточно времени
            blocked_users[chat_id][user_id]["time"] = current_time
            blocked_users[chat_id][user_id]["warnings"] = 0

        return await handler(event, data)
