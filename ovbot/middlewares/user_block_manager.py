import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)
blocked_users = defaultdict(dict)

def is_user_blocked(chat_id, user_id):
    user_data = blocked_users.get(chat_id, {}).get(user_id)
    if not user_data or "blocked_until" not in user_data:
        return False
    return user_data["blocked_until"] > time.time()

def block_user(chat_id, user_id, duration, reason=""):
    current_time = time.time()
    blocked_until = current_time + duration
    blocked_users[chat_id][user_id] = {
        "blocked_until": blocked_until,
        "reason": reason,
        "warnings": 0,
    }
    logger.info(f"Менеджер блокировок: Пользователь {user_id} заблокирован до {blocked_until}.")

def add_user_warning(chat_id, user_id):
    if chat_id not in blocked_users:
        blocked_users[chat_id] = {}
    if user_id not in blocked_users[chat_id]:
        blocked_users[chat_id][user_id] = {"warnings": 0}
    blocked_users[chat_id][user_id]["warnings"] += 1
    logger.debug(f"Менеджер блокировок: Пользователь {user_id} получил предупреждение.")

def get_user_warnings(chat_id, user_id):
    """Возвращает количество предупреждений пользователя."""
    return blocked_users.get(chat_id, {}).get(user_id, {}).get("warnings", 0)


def reset_warnings(chat_id, user_id):
    """Обнуляет количество предупреждений для пользователя."""
    if chat_id in blocked_users and user_id in blocked_users[chat_id]:
        blocked_users[chat_id][user_id]["warnings"] = 0
        logger.info(f"Сброшены предупреждения для пользователя {user_id} в чате {chat_id}.")