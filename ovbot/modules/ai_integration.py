import os
import json
from datetime import datetime
from modules.token_manager import TokenManager
from config import YANDEX_OAUTH_TOKEN, YCLOUD_CATALOG_ID
from config import WHO_IS_BOT, DIALOGS_DIR
import requests


os.makedirs(DIALOGS_DIR, exist_ok=True)


token_manager = TokenManager(YANDEX_OAUTH_TOKEN)


def get_dialog_filename(username, user_id, chat_id):
    """Формирует имя файла для хранения диалога по пользователю и чату."""
    return os.path.join(DIALOGS_DIR, f"{username}_{user_id}_{chat_id}.json")


def load_dialog_history(filename):
    """Загружает историю диалога из файла."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_dialog_history(filename, dialog_history):
    """Сохраняет историю диалога в файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dialog_history, file, ensure_ascii=False, indent=2)


def gpt(data):
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "x-data-logging-enabled": "false"
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise RuntimeError(f'Ошибка: код {response.status_code}, сообщение: {response.text}')

    response_json = response.json()
    try:
        return response_json["result"]["alternatives"][0]["message"]["text"]
    except (KeyError, IndexError):
        return "Ответ не найден"


def process_ai_response(user_id, chat_id, username, user_message):
    filename = get_dialog_filename(username, user_id, chat_id)
    dialog_history = load_dialog_history(filename)
    if not any(msg["role"] == "system" for msg in dialog_history):
        dialog_history.insert(0, {
            "role": "system",
            "text": WHO_IS_BOT
        })
    dialog_history.append({"role": "user", "text": user_message})

    data = {
        "modelUri": f"gpt://{YCLOUD_CATALOG_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": dialog_history
    }
    assistant_response = gpt(data)
    dialog_history.append({"role": "assistant", "text": assistant_response})
    save_dialog_history(filename, dialog_history)

    return assistant_response
