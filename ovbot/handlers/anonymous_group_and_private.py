from aiogram import Router, types
from config import TELEGRAM_GROUP_ID, endpoint_tg_users
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                security_filters)
from inits.api_client import api_ov_client
from utils.security import crypt
from utils.user_utils import get_level_rang

anonymous_group_and_private_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel", "private"]),
    UserLevelFilter(0, 100, "IsAnonymousUser"),
]


@security_filters(anonymous_group_and_private_router, "start", *common_filters)
async def start(message: types.Message):
    try:
        user_response = await api_ov_client.get(
            f"{endpoint_tg_users}?tg_user_id={crypt(message.from_user.id)}"
        )
        if user_response["count"] > 0:
            user_in_bd = user_response["results"][0]["tg_user_id"]
            if crypt(message.from_user.id) == user_in_bd:
                await message.answer(
                    f"@{message.from_user.username}, "
                    f"нельзя регистрироваться повторно!"
                )
                return

        api_data = {
            "tg_user_id": crypt(message.from_user.id),
            "tg_first_name": message.from_user.first_name,
            "tg_last_name": message.from_user.last_name,
            "tg_user_name": message.from_user.username,
            "ban_status": False,
            "level": 15,
        }
        await api_ov_client.post(endpoint_tg_users, api_data)
        await message.answer(
            f"Привет, @{message.from_user.username}! "
            f"Вы успешно зарегистрированы"
        )

        user_count_response = await api_ov_client.get(endpoint_tg_users)
        user_count = user_count_response["count"]

        await message.bot.send_message(
            chat_id=TELEGRAM_GROUP_ID,
            text=f"Новый пользователь зарегистрирован:\n"
            f"Имя: {message.from_user.first_name} "
            f"{message.from_user.last_name}\n"
            f"Имя пользователя: @{message.from_user.username}\n"
            f"Всего пользователей в базе данных: {user_count}",
        )

    except ValueError:
        await message.answer("Произошла ошибка при обработке ID пользователя.")
    except KeyError:
        await message.answer(
            "Произошла ошибка при доступе к данным " "пользователя."
        )
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


@security_filters(
    anonymous_group_and_private_router, "status", *common_filters
)
async def show_status(message: types.Message):
    try:
        tg_user_id = crypt(message.from_user.id)
        user_response = await api_ov_client.get(
            f"{endpoint_tg_users}?tg_user_id={tg_user_id}"
        )
        if user_response["count"] == 0:
            level_rang = get_level_rang(16)
            await message.answer(f"Ваш уровень: {level_rang}")
            return

        user_data = user_response["results"][0]
        user_level = user_data["level"]
        level_rang = get_level_rang(user_level)

        await message.answer(f"Ваш уровень: {level_rang}")
    except ValueError:
        await message.answer("Произошла ошибка при обработке ID пользователя.")
    except KeyError:
        await message.answer(
            "Произошла ошибка при доступе к данным пользователя."
        )
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
