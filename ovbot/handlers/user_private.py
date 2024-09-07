from aiogram import types, Router

from datetime import datetime

from filters.chat_types import (
    UserLevelFilter,
    ChatTypesFilter,
    security_filters
)


user_private_router = Router()
common_filters = [
    ChatTypesFilter(['private']),
    UserLevelFilter(0, 15, 'IsAuthUser')
]


@security_filters(user_private_router, 'time', *common_filters)
async def show_time(message: types.Message):
    today = datetime.today()
    await message.answer(f'{today}')
