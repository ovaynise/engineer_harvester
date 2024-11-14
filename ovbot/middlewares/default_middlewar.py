import json
import os
import time
from datetime import datetime
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, Update, ChatPermissions, ChatMember
from collections import defaultdict
from config import logger_other, TELEGRAM_GROUP_ID, logger_bot
from utils.security import crypt
from utils.user_utils import get_user_level

INITIAL_BLOCK_DURATION = 1
SECOND_BLOCK_DURATION = 5
SUBSEQUENT_BLOCK_DURATION = 30


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, rate_limit: int = 2, warning_limit: int = 2):
        super().__init__()
        self.bot = bot
        self.rate_limit = rate_limit
        self.warning_limit = warning_limit
        self.user_last_message = defaultdict(
            lambda: {"time": 0, "warnings": 0, "blocked_until": 0,
                     "block_count": 0})

    async def __call__(self, handler, event: Update, data: dict):
        if isinstance(event, Update) and event.message and isinstance(
                event.message, Message):
            message = event.message
            user_id = message.from_user.id
            chat_id = message.chat.id
            current_time = time.time()
            member = await self.bot.get_chat_member(chat_id, user_id)
            user_level = await get_user_level(crypt(user_id))
            if member.status in {"administrator",
                                 "creator"} or user_level == 0:
                return await handler(event, data)
            last_activity = self.user_last_message[user_id]
            if current_time < last_activity["blocked_until"]:
                block_end_time = datetime.fromtimestamp(
                    last_activity["blocked_until"]).strftime(
                    '%Y-%m-%d %H:%M:%S')
                if message.chat.type == "private" and not last_activity.get(
                        "block_notified", False):
                    await message.reply(
                        f"Вы были временно заблокированы до {block_end_time}.")
                    self.user_last_message[user_id]["block_notified"] = True
                return
            if current_time - last_activity["time"] < self.rate_limit:
                last_activity["warnings"] += 1
                if last_activity["warnings"] >= self.warning_limit:
                    block_count = last_activity["block_count"]
                    block_duration = INITIAL_BLOCK_DURATION * 60 if block_count == 0 else SECOND_BLOCK_DURATION * 60 if block_count == 1 else SUBSEQUENT_BLOCK_DURATION * 60
                    block_end_time = current_time + block_duration
                    readable_block_end = datetime.fromtimestamp(
                        block_end_time).strftime('%Y-%m-%d %H:%M:%S')
                    await message.reply(
                        f"{message.from_user.username}, вы были временно заблокированы за спам до {readable_block_end}.")
                    if message.chat.type == 'supergroup':
                        await self.bot.restrict_chat_member(
                            chat_id, user_id,
                            permissions=ChatPermissions(
                                can_send_messages=False),
                            until_date=block_end_time
                        )
                    else:
                        logger_bot.warning(
                            f"Попытка заблокировать пользователя в обычной группе: {message.chat.id}")
                    await self.bot.send_message(
                        TELEGRAM_GROUP_ID,
                        f"Пользователь @{message.from_user.username} (ID: {user_id}) заблокирован за спам.\n"
                        f"Причина: Спам сообщений.\n"
                        f"Заблокирован до: {readable_block_end}\n"
                        f"Чат: {message.chat.title if message.chat.title else 'Без названия'}"
                    )
                    self.user_last_message[user_id] = {
                        "time": current_time,
                        "warnings": 0,
                        "blocked_until": block_end_time,
                        "block_notified": False,
                        "block_count": block_count + 1
                    }
                else:
                    await message.reply(
                        f"{message.from_user.username}, пожалуйста,"
                        f" не спамьте.")
                return
            self.user_last_message[user_id]["time"] = current_time
            self.user_last_message[user_id]["warnings"] = 0

        return await handler(event, data)


class ForbiddenWordsMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, banwords_file_path: str):
        super().__init__()
        self.bot = bot
        self.banned_words = self.load_banwords(banwords_file_path)
        self.user_last_warning = defaultdict(lambda: {"warnings": 0,
                                                      "blocked_until": 0})
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
            user_id = message.from_user.id
            chat_id = message.chat.id
            current_time = time.time()
            if user_id in self.user_last_warning:
                block_end_time = self.user_last_warning[user_id]["blocked_until"]
                if block_end_time > current_time:
                    if message.chat.type == "private" and not self.user_last_warning[user_id].get("block_notified", False):
                        readable_block_end = datetime.fromtimestamp(block_end_time).strftime('%Y-%m-%d %H:%M:%S')
                        await message.reply(f"Вы заблокированы до {readable_block_end}. Повторное нарушение приведет к более длительной блокировке.")
                        self.user_last_warning[user_id]["block_notified"] = True
                    return
            if message.text and any(word in message.text.lower() for word in self.banned_words):
                warnings = self.user_last_warning[user_id]["warnings"]
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
                        logger_other.error(f"Не удалось заблокировать "
                                           f"пользователя {user_id} в чате "
                                           f"{chat_id}: {e}")
                    self.user_last_warning[user_id]["blocked_until"] = block_end_time
                    await self.bot.send_message(
                        TELEGRAM_GROUP_ID,
                        f"Пользователь @{message.from_user.username} "
                        f"заблокирован за использование запрещённых слов.\n"
                        f"Чат: {message.chat.title if message.chat.title else 'Без названия'}\n"
                        f"Причина: Нецензурные слова.\n"
                        f"Заблокирован до: {readable_block_end}"
                    )
                    if message.chat.type == "private":
                        await message.reply(f"Вы были заблокированы до {readable_block_end} за использование запрещённых слов.")

                    return
                self.user_last_warning[user_id]["warnings"] += 1

                remaining_warnings = 2 - self.user_last_warning[user_id]["warnings"]
                await message.reply(f"{message.from_user.username}, ваше сообщение содержит запрещённые слова. "
                                     f"У вас осталось {remaining_warnings} предупреждений.")
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
