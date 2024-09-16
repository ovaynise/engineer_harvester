import asyncio
from typing import Dict

from aiogram import Router, types
from config import TELEGRAM_GROUP_ID
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                UserLevelRangeFilter, security_filters)
from inits.ai_client import ai_assistant
from inits.logger import bot_logger
from utils.security import crypt
from utils.user_utils import (add_activity_chat_for_reminder,
                              del_activity_chat_for_reminder,
                              get_reminder_by_id)

group_and_private_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel", "private"]),
    UserLevelFilter(0, 15, "IsAuthUser"),
]


@security_filters(
    group_and_private_router,
    None,
    UserLevelRangeFilter(min_level=0, max_level=15),
    *common_filters,
)
async def ai_reply(message: types.Message):
    bot_logger.debug("Отработала функция ai_reply")
    user_text = message.text

    await asyncio.sleep(0.5)
    await message.answer(f"{ai_assistant.show_ai_answer(user_text)}")
    await message.bot.send_message(
        chat_id=TELEGRAM_GROUP_ID,
        text=f"@{message.from_user.username} "
             f"- {message.from_user.first_name}"
             f"- {message.from_user.last_name}:\n"
             f"{message.chat.title}\n"
             f"Запрошен текст:➡️' {user_text}'"
    )


@security_filters(group_and_private_router, "id", *common_filters)
async def show_id(message: types.Message):
    bot_logger.debug("Отработала функция id")
    await message.answer(
        f"Ваш id: {message.from_user.id}, "
        f"id чата: {message.chat.id}, "
        f"id темы: {message.message_thread_id}"
    )


@security_filters(group_and_private_router, "старт", *common_filters)
async def handle_start_reminder_id(message: types.Message):
    command_parts = message.text.split(maxsplit=1)
    await message.delete()
    if len(command_parts) < 2:
        await message.answer(
            "Пожалуйста, "
            "укажите номер напоминания "
            "после команды '/старт'."
        )
        return
    reminder_id_str = command_parts[1]
    if not reminder_id_str.isdigit():
        await message.answer("Номер напоминания должен быть целым числом.")
        return
    reminder_id = int(reminder_id_str)
    chat_name = (
        message.chat.title
        if message.chat.title
        else message.from_user.first_name
    )
    owner_reminder_id = crypt(message.from_user.id)
    rem_data = {"status_reminder": True, "chats_id_active": {}}
    rem_data["chats_id_active"][message.chat.id] = chat_name
    try:
        reminder = await get_reminder_by_id(reminder_id)
        if reminder and reminder["owner_reminder_id"] == owner_reminder_id:
            await add_activity_chat_for_reminder(reminder_id, rem_data)
            await message.answer(
                f"Напоминание "
                f"ID{reminder_id} успешно запущено "
                f"в чате: {chat_name}"
            )
        else:
            await message.answer(f"У вас нет напоминания с ID : {reminder_id}")

    except Exception as e:
        bot_logger.error(f"Получена ошибка: {e}")


@security_filters(group_and_private_router, "стоп", *common_filters)
async def handle_stop_reminder_id(message: types.Message):
    command_parts = message.text.split(maxsplit=1)
    await message.delete()
    if len(command_parts) < 2:
        await message.answer(
            "Пожалуйста, укажите номер " "напоминания после команды '/стоп'."
        )
        return
    reminder_id_str = command_parts[1]
    if not reminder_id_str.isdigit():
        await message.answer("Номер напоминания должен быть целым числом.")
        return
    reminder_id = int(reminder_id_str)
    chat_name = (
        message.chat.title
        if (message.chat.title)
        else {message.from_user.first_name}
    )
    owner_reminder_id = crypt(message.from_user.id)
    rem_data: Dict[str, Dict] = {"chats_id_active": {}}
    rem_data["chats_id_active"][str(message.chat.id)] = chat_name

    try:
        reminder = await get_reminder_by_id(reminder_id)
        if reminder and reminder["owner_reminder_id"] == owner_reminder_id:
            await del_activity_chat_for_reminder(reminder_id, rem_data)
            await message.answer(
                f"Напоминание "
                f"ID{reminder_id} успешно остановлено "
                f"в чате: {chat_name}"
            )
        else:
            await message.answer(f"У вас нет напоминания с ID : {reminder_id}")

    except ValueError:
        await message.answer(
            "Вы не являетесь владельцем "
            "этого напоминания и не можете его остановить."
        )
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
