from functools import wraps
from typing import Callable
from aiogram.types import Message
from aiogram import Router, types
from aiogram.filters import Command, Filter
from config import logger_bot
from utils.security import crypt
from utils.user_utils import get_user_level
from aiogram import Bot



def log_filter_result(
    command: str,
    username: str,
    user_firstname: str,
    chat_title: str,
    chat_type: str,
    filter_name: str,
    result: bool,
    user_level: int = None,
):
    status = "🟡" if result else "🔴"
    user_info = (
        f"Пользователь @{username} ({user_firstname}) в чате "
        f"{chat_title} ({chat_type})."
    )
    level_info = (
        f" Уровень пользователя {user_level}."
        if user_level is not None
        else ""
    )
    logger_bot.debug(
        f'{status}Команда "/{command}": Фильтр {filter_name}: '
        f'доступ {"разрешен" if result else "запрещен"}.\n'
        f"{user_info}{level_info}"
    )


def security_filters(router: Router, command: str = None, *filters: Filter):
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(message: types.Message):
            username = message.from_user.username or "неизвестен"
            user_firstname = message.from_user.first_name
            chat_title = message.chat.title or f"личный чат ({message.chat.id})"
            user_id = message.from_user.id

            # Отладка для типа чата и команды
            print(f"Processing command: /{command or 'Сообщение'} in chat type: {message.chat.type}")

            for filter_ in filters:
                if not await filter_(
                    message,
                    command,
                    username,
                    user_id,
                    user_firstname,
                    chat_title,
                ):
                    return  # Фильтр не пройден, выход

            logger_bot.debug(f"🟢 Фильтры пройдены для пользователя {username}")
            return await handler(message)

        # Регистрация команды или сообщений без команды
        if command:
            router.message.register(wrapper, Command(command))
        else:
            router.message.register(wrapper)

        return handler

    return decorator


class ChatTypesFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(
            self,
            message: types.Message,
            command: str = None,
            username: str = "",
            user_id: int = 0,
            user_firstname: str = "",
            chat_title: str = "",
    ) -> bool:
        # Логирование для диагностики типа чата
        logger_bot.info(
            f"Проверка типа чата: {message.chat.type} для команды /{command or 'Сообщение'}")

        # Проверка типа чата на соответствие разрешенным типам
        result = message.chat.type in self.chat_types
        if not result:
            # Сообщение об ошибке и логирование
            await message.answer(
                f"Команда /{command or 'неизвестная'} доступна только в "
                f"следующих типах чатов: {', '.join(self.chat_types)}."
            )
        log_filter_result(
            command or "Сообщение",
            username,
            user_firstname,
            chat_title,
            message.chat.type,
            "ChatTypesFilter",
            result,
        )
        return result


class UserLevelFilter(Filter):
    def __init__(
        self, min_level: int, max_level: int, filter_name: str
    ) -> None:
        self.min_level = min_level
        self.max_level = max_level
        self.filter_name = filter_name

    async def __call__(
        self,
        message: types.Message,
        command: str,
        username: str,
        user_id: int,
        user_firstname: str,
        chat_title: str,
    ) -> bool:
        user_level = await get_user_level(crypt(user_id))
        result = (
            user_level is not None
            and self.min_level <= user_level <= self.max_level
        )
        if not result:
            if user_level is None:
                await message.answer(
                    f"Для выполнения команды /{command} "
                    f"необходимо зарегистрироваться. "
                    f"Введите /start для регистрации."
                )
            else:
                await message.answer(
                    f"Для выполнения команды /{command} "
                    f"необходим уровень доступа "
                    f"от {self.min_level} до {self.max_level}"
                    f". Ваш уровень: {user_level}."
                )
        log_filter_result(
            command,
            username,
            user_firstname,
            chat_title,
            message.chat.type,
            self.filter_name,
            result,
            user_level,
        )
        return result


class IsAnonymousUser(Filter):
    async def __call__(
        self,
        message: types.Message,
        command: str,
        username: str,
        user_id: int,
        user_firstname: str,
        chat_title: str,
    ) -> bool:
        if message.from_user.is_bot or message.from_user.id is None:
            logger_bot.debug(
                f'🟡Команда "/{command}": Фильтр '
                f"IsAnonymousUser: пользователь анонимен или бот.\n"
                f"Пользователь @{username} ({user_firstname}) в "
                f"чате {chat_title}."
            )
            await message.answer(
                f"Команда /{command} не доступна для "
                f"анонимных пользователей или ботов."
            )
            return False
        return True


class UserLevelRangeFilter(Filter):
    def __init__(self, min_level: int, max_level: int) -> None:
        self.min_level = min_level
        self.max_level = max_level

    async def __call__(
            self,
            message: types.Message,
            command: str,
            username: str,
            user_id: int,
            user_firstname: str,
            chat_title: str,
    ) -> bool:
        # Проверка для reply или упоминания бота
        if not (message.reply_to_message or
                any(entity.type == "mention" and entity.extract_text(
                    message.text) == f'@{message.bot.username}' for entity in
                    message.entities)):
            return False

        user_level = await get_user_level(crypt(user_id))
        result = (
                user_level is not None
                and self.min_level <= user_level <= self.max_level
        )

        if not result:
            await message.answer(
                f"Для общения с ботом необходимо быть "
                f"с уровнем доступа от {self.min_level} "
                f"до {self.max_level}. "
                f" Ваш уровень: {user_level}. "
                f"Для получения 15 уровня зарегистрируйтесь "
                f"командой /start"
            )
        return result


class UserPrivateLevelRangeFilter(Filter):
    def __init__(self, min_level: int, max_level: int) -> None:
        self.min_level = min_level
        self.max_level = max_level

    async def __call__(
        self,
        message: types.Message,
        command: str,
        username: str,
        user_id: int,
        user_firstname: str,
        chat_title: str,
    ) -> bool:
        user_level = await get_user_level(crypt(user_id))
        result = (
            user_level is not None
            and self.min_level <= user_level <= self.max_level
        )
        if not result:
            await message.answer(
                f"Для общения с ботом необходимо быть "
                f"с уровнем доступа от {self.min_level} "
                f"до {self.max_level}. "
                f"Ваш уровень: {user_level}. "
                f"Для получения 15 уровня зарегистрируйтесь "
                f"командой /start"
            )
        return result

class GroupChatInteractionFilter(Filter):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(self, message: Message, *args, **kwargs) -> bool:
        bot_username = (await self.bot.get_me()).username

        # Проверка на реплай на сообщение бота
        is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == self.bot.id

        # Проверка на упоминание бота в тексте
        mentions_bot = message.entities and any(
            entity.type == "mention" and
            message.text[entity.offset:entity.offset + entity.length] == f"@{bot_username}"
            for entity in message.entities
        )

        # Возвращаем True только если сообщение направлено боту (реплай или упоминание)
        return is_reply_to_bot or mentions_bot