from config import LEVEL_RANGS, endpoint_reminder, endpoint_tg_users
from inits.api_client import api_ov_client
from inits.logger import bot_logger, db_logger
from utils.security import crypt


async def check_and_register_user(message):
    try:
        tg_user_id = crypt(message.from_user.id)
        user_response = await api_ov_client.get(
            f"{endpoint_tg_users}?tg_user_id={tg_user_id}"
        )
        if user_response["count"] > 0:
            return False, None
        api_data = {
            "tg_user_id": tg_user_id,
            "tg_first_name": message.from_user.first_name,
            "tg_last_name": message.from_user.last_name,
            "tg_user_name": message.from_user.username,
            "ban_status": False,
            "level": 15,
        }
        await api_ov_client.post(endpoint_tg_users, api_data)
        return True, (
            f"Привет, "
            f"@{message.from_user.username}! Вы успешно "
            f"зарегистрированы"
        )
    except ValueError:
        db_logger.error("Произошла ошибка при обработке ID пользователя.")
        return False, "Произошла ошибка при обработке ID пользователя."
    except KeyError:
        db_logger.error("Произошла ошибка при доступе к данным пользователя.")
        return False, "Произошла ошибка при доступе к данным пользователя."
    except Exception as e:
        db_logger.error(f"Произошла ошибка: {e}")
        return False, f"Произошла ошибка: {e}"


async def update_user_level(message, new_level):
    try:
        tg_user_id = crypt(message.from_user.id)
        user_response = await api_ov_client.get(
            f"{endpoint_tg_users}?tg_user_id={tg_user_id}"
        )

        if user_response["count"] == 0:
            return False, "Пользователь не найден."

        user_data = user_response["results"][0]
        user_id = user_data["id"]

        update_data = {"level": new_level}
        await api_ov_client.patch(
            f"{endpoint_tg_users}{user_id}/", update_data
        )
        return True, f"Ваш уровень успешно обновлен до {new_level}"

    except ValueError:
        db_logger.error("Произошла ошибка при обработке ID пользователя.")
        return False, "Произошла ошибка при обработке ID пользователя."
    except KeyError:
        db_logger.error("Произошла ошибка при доступе к данным пользователя.")
        return False, "Произошла ошибка при доступе к данным пользователя."
    except Exception as e:
        db_logger.error(f"Произошла ошибка: {e}")
        return False, f"Произошла ошибка: {e}"


def get_level_rang(level):
    for key, value in LEVEL_RANGS.items():
        if isinstance(key, tuple):
            if level in key:
                return value
        elif key == level:
            return value
    return "UNKNOWN"


async def get_user_data(tg_user_id):
    try:
        response = await api_ov_client.get(
            f"{endpoint_tg_users}?tg_user_id={tg_user_id}"
        )
        if response["count"] > 0:
            return response["results"][0]
        return None
    except Exception as e:
        bot_logger.error(f"Ошибка при получении данных пользователя: {e}")
        return None


async def get_user_level(tg_user_id):
    try:
        user_response = await api_ov_client.get(
            f"{endpoint_tg_users}?tg_user_id={tg_user_id}"
        )
        if user_response["count"] > 0:
            user_level = user_response["results"][0]["level"]
            return user_level
        else:
            return 16
    except Exception as e:
        bot_logger.error(f"Ошибка при получении уровня пользователя: {e}")
        return None


async def get_reminder_by_id(reminder_id):
    try:
        reminder_response = await api_ov_client.get(
            f"{endpoint_reminder}{reminder_id}/"
        )
        if reminder_response is None:
            return False
        if reminder_response["id"] == reminder_id:
            return reminder_response
        else:
            return False
    except Exception as e:
        bot_logger.error(f"Ошибка : {e}")
        return None


async def add_activity_chat_for_reminder(reminder_id, data):
    try:
        response = await get_reminder_by_id(reminder_id)
        response["chats_id_active"].update(data.get("chats_id_active", {}))
        updated_data = {
            "status_reminder": True,
            "chats_id_active": response["chats_id_active"],
        }
        await api_ov_client.patch(endpoint_reminder, updated_data, reminder_id)
    except Exception as e:
        bot_logger.error(f"Ошибка: {e}")
        return None


async def del_activity_chat_for_reminder(reminder_id, data):
    try:

        response = await get_reminder_by_id(reminder_id)

        current_chats_active = response.get("chats_id_active", {})

        chats_to_remove = data.get("chats_id_active", {})
        print(f"chats_to_remove{chats_to_remove}")

        for chat_id in chats_to_remove.keys():
            if chat_id in current_chats_active:
                del current_chats_active[chat_id]

        status_reminder = bool(current_chats_active)

        updated_data = {
            "status_reminder": status_reminder,
            "chats_id_active": current_chats_active,
        }

        await api_ov_client.patch(endpoint_reminder, updated_data, reminder_id)

    except Exception as e:
        bot_logger.error(f"Ошибка: {e}")
        return None
