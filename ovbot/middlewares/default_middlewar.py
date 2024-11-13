import json
import os

from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from config import logger_other
from utils.security import crypt
from utils.user_utils import get_user_level


class ForbiddenWordsMiddleware(BaseMiddleware):
    def __init__(self, banwords_file_path: str):
        super().__init__()
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
        if isinstance(event, Update) and event.message and isinstance(
                event.message, Message):
            message = event.message
            if message.text:
                logger_other.info(f"Получено сообщение: {message.text}")
                if any(word in message.text.lower() for word in
                       self.banned_words):
                    logger_other.info(
                        f"Найдено запрещенное слово в сообщении:"
                        f" {message.text}")
                    await message.reply(
                        f"{message.from_user.username}, пожалуйста,"
                        f" соблюдайте правила чата!")
                    return
        return await handler(event, data)


class AccessControlMiddleware(BaseMiddleware):
    def __init__(self, min_level: int = 0, max_level: int = 15):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    async def __call__(self, handler, event: Update, data: dict):
        if (isinstance(event,
                       Update) and event.message and isinstance(event.message,
                                                                Message)):
            message = event.message
            user_id = message.from_user.id
            if (message.text.startswith("/status") or message.text.startswith(
                    "/start")):
                return await handler(event, data)
            user_level = await get_user_level(crypt(user_id))

            if user_level is None:
                await message.answer("Для доступа необходимо"
                                     " зарегистрироваться. Введите "
                                     "/start для регистрации.")
                return

            elif not (self.min_level <= user_level <= self.max_level):
                await message.answer(
                    f"Недостаточно прав. Ваш уровень: {user_level}."
                    f" Необходимо от {self.min_level} до {self.max_level}. "
                    f"Введите команду /start для регистрации."
                )
                return
        return await handler(event, data)
