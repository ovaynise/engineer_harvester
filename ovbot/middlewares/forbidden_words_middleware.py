import logging
import os
import json
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, Update, ChatPermissions
from middlewares.user_block_manager import is_user_blocked, block_user, add_user_warning, get_user_warnings, reset_warnings
from middlewares.ban_manager_middleware import restrict_user
import time

logger = logging.getLogger(__name__)

class ForbiddenWordsMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, banwords_file_path: str):
        super().__init__()
        self.bot = bot
        self.banned_words = self.load_banwords(banwords_file_path)

    def load_banwords(self, file_path: str):
        if not os.path.exists(file_path):
            logger.warning(f"Антимат: Файл '{file_path}' не найден.")
            return []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Антимат: Загружено {len(data)} запрещённых слов.")
            return [entry['word'].lower() for entry in data]
        except Exception as e:
            logger.error(f"Антимат: Ошибка загрузки файла {file_path}: {e}")
            return []

    async def __call__(self, handler, event: Update, data: dict):
        if isinstance(event, Update) and event.message and isinstance(event.message, Message):
            message = event.message
            user_id = message.from_user.id
            chat_id = message.chat.id

            # Проверяем наличие запрещённых слов
            if any(word in message.text.lower() for word in self.banned_words):
                add_user_warning(chat_id, user_id)
                warnings = get_user_warnings(chat_id, user_id)
                logger.warning(f"Антимат: Пользователь {user_id} получил предупреждение ({warnings}/3).")

                if warnings >= 3:
                    await restrict_user(self.bot, chat_id, user_id, warnings, reset_warnings)
                    return

                await message.reply(f"{message.from_user.username}, это предупреждение. Осталось {3 - warnings}.")
        return await handler(event, data)