from aiogram import Router, types
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                security_filters)
from utils.security import crypt
from utils.user_utils import check_and_register_user, update_user_level

admin_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel", "private"]),
    UserLevelFilter(0, 4, "IsAdmin"),
]


@security_filters(admin_router, "setlevel", *common_filters)
async def set_level(message: types.Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            await message.answer(
                "Пожалуйста, укажите корректный уровень "
                "(от 1 до 15). Пример: /setlevel 5"
            )
            return

        new_level = int(command_parts[1])
        if new_level < 1 or new_level > 15:
            await message.answer("Уровень должен быть в диапазоне от 1 до 15.")
            return
    except (IndexError, ValueError):
        await message.answer(
            "Пожалуйста, укажите корректный уровень (от 1 до 15)."
            "Пример: /setlevel 5"
        )
        return

    user_id = message.from_user.id
    encrypted_user_id = crypt(user_id)

    is_registered, response_message = await check_and_register_user(
        encrypted_user_id
    )
    if not is_registered:
        await message.answer(response_message)
        return

    success, response_message = await update_user_level(
        encrypted_user_id, new_level
    )
    if success:
        await message.answer(
            f"Уровень пользователя успешно обновлен до {new_level}."
        )
    else:
        await message.answer(response_message)
