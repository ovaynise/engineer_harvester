from middlewares.blocked_users import blocked_users
import json
import os
import time
from datetime import datetime
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, Update, ChatPermissions
from config import logger_other, TELEGRAM_GROUP_ID


INITIAL_BLOCK_DURATION = 1
SECOND_BLOCK_DURATION = 5
SUBSEQUENT_BLOCK_DURATION = 30

class ForbiddenWordsMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, banwords_file_path: str):
        super().__init__()
        self.bot = bot
        self.banned_words = self.load_banwords(banwords_file_path)

    def load_banwords(self, file_path: str):
        """Загружаем список плохих слов из JSON файла."""
        if not os.path.exists(file_path):
            logger_other.info(f"Ошибка: файл '{file_path}' не найден.")
            return []

        try:
            logger_other.info(f"Загружаем файл с плохими словами: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            banned_words = [entry['word'].lower() for entry in data]
            logger_other.info(f"Загружено {len(banned_words)} слов из файла.")
            return banned_words
        except Exception as e:
            logger_other.info(f"Ошибка при загрузке слов из JSON: {e}")
            return []

    async def __call__(self, handler, event: Update, data: dict):
        if isinstance(event, Update) and event.message and isinstance(event.message, Message):
            message = event.message
            user_id = message.from_user.id
            chat_id = message.chat.id
            current_time = time.time()

            # Проверка, заблокирован ли пользователь в этом чате
            if chat_id in blocked_users and user_id in blocked_users[chat_id]:
                block_end_time = blocked_users[chat_id][user_id]["blocked_until"]
                if block_end_time > current_time:
                    if message.chat.type == "private" and not blocked_users[chat_id][user_id].get("block_notified", False):
                        readable_block_end = datetime.fromtimestamp(block_end_time).strftime('%Y-%m-%d %H:%M:%S')
                        await message.reply(f"Вы заблокированы до {readable_block_end}.")
                        blocked_users[chat_id][user_id]["block_notified"] = True
                    return  # Игнорируем сообщения до окончания блокировки

            # Проверка на запрещенные слова
            if message.text and any(word in message.text.lower() for word in self.banned_words):
                warnings = blocked_users[chat_id].get(user_id, {}).get("warnings", 0)
                if warnings >= 2:
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
                        "reason": "bad_words",
                        "block_notified": False
                    }

                    # Отправляем сообщение в группу
                    await self.bot.send_message(
                        TELEGRAM_GROUP_ID,
                        f"Пользователь @{message.from_user.username} заблокирован за использование запрещённых слов.\n"
                        f"Чат: {message.chat.title if message.chat.title else 'Без названия'}\n"
                        f"Причина: Нецензурные слова.\n"
                        f"Заблокирован до: {readable_block_end}"
                    )

                    # Отправляем сообщение в личку
                    if message.chat.type == "private":
                        await message.reply(f"Вы были заблокированы до {readable_block_end} за использование запрещённых слов.")

                    return  # Больше не реагируем на пользователя

                # Увеличиваем количество предупреждений
                if chat_id not in blocked_users:
                    blocked_users[chat_id] = {}

                blocked_users[chat_id].setdefault(user_id, {"warnings": 0})
                blocked_users[chat_id][user_id]["warnings"] += 1

                remaining_warnings = 2 - blocked_users[chat_id][user_id]["warnings"]
                await message.reply(f"{message.from_user.username}, ваше сообщение содержит запрещённые слова. У вас осталось {remaining_warnings} предупреждений.")
                return

        return await handler(event, data)