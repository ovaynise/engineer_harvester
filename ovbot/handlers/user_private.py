from datetime import datetime

from aiogram import Router, types
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                security_filters, UserPrivateLevelRangeFilter)
from modules.ai_integration import process_ai_response


user_private_router = Router()

common_filters = [
    ChatTypesFilter(["private"]),
    UserLevelFilter(0, 15, "IsAuthUser"),
]


def setup_user_private_handlers(ovay_bot):
    @security_filters(user_private_router, "time", *common_filters)
    async def show_time(message: types.Message):
        today = datetime.today()
        await message.answer(f"{today}")

    @security_filters(
        user_private_router,
        None,
        UserPrivateLevelRangeFilter(min_level=0, max_level=15),
        *common_filters,
    )
    async def ai_or_log_message(msg: types.Message):
        user_message = msg.text
        user_id = msg.from_user.id
        chat_id = msg.chat.id
        username = msg.from_user.username or "Без имени"
        chat_title = msg.chat.title if msg.chat.title else username
        bot_message = process_ai_response(user_id, chat_id, username,
                                          user_message)
        await ovay_bot.info_message(
            chat_id=chat_id,
            bot_message=bot_message,
            user_message=user_message,
            user_id=user_id,
            username=username,
            chat_title=chat_title
        )

    return user_private_router

