from aiogram import Router, types
from config import logger_bot
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                security_filters)


group_and_private_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel", "private"]),
    UserLevelFilter(0, 15, "IsAuthUser"),
]


def setup_group_and_private_handlers(ovay_bot):
    @security_filters(group_and_private_router, "id", *common_filters)
    async def show_id(message: types.Message):
        logger_bot.debug("Отработала функция id")
        await message.answer(
            f"Ваш id: {message.from_user.id}, "
            f"id чата: {message.chat.id}, "
            f"id темы: {message.message_thread_id}"
        )

    return group_and_private_router


