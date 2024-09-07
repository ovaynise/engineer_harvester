from aiogram import Router, types
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                security_filters)
from inits.ai_client import ai_assistant

super_user_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel", "private"]),
    UserLevelFilter(0, 0, "IsSuperUser"),
]


@security_filters(super_user_router, "su", *common_filters)
async def su_test(message: types.Message):
    await message.answer(
        f"SUPERUSER, подтвержен: " f"{message.from_user.username}"
    )


@security_filters(super_user_router, "ai", *common_filters)
async def ai_info(message: types.Message):
    await message.answer(f"Ваш баланс: " f"{ai_assistant.show_balance()} RUB")
