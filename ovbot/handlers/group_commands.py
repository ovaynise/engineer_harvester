from aiogram import Router
from filters.chat_types import ChatTypesFilter, UserLevelFilter

group_commands_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel"]),
    UserLevelFilter(0, 15, "IsAuthUser"),
]
