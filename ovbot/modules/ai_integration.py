import json
import os
from cryptography.fernet import Fernet
import requests
from config import (DIALOGS_DIR, WHO_IS_BOT, YANDEX_OAUTH_TOKEN,
                    YCLOUD_CATALOG_ID, ENCRYPT_SALT)
from modules.token_manager import TokenManager

# Убедитесь, что DIALOGS_DIR существует
os.makedirs(DIALOGS_DIR, exist_ok=True)

token_manager = TokenManager(YANDEX_OAUTH_TOKEN)

# Создаем объект Fernet для шифрования и расшифровки
fernet = Fernet(ENCRYPT_SALT)


def encrypt_data(data):
    """Шифрует данные перед сохранением."""
    return fernet.encrypt(data.encode())


def decrypt_data(data):
    """Расшифровывает данные перед загрузкой."""
    return fernet.decrypt(data).decode()


def get_dialog_filename(user_id):
    """Формирует имя файла для хранения диалога по пользователю."""
    return os.path.join(DIALOGS_DIR, f"{user_id}.json")


def load_dialog_history(filename):
    """Загружает и расшифровывает историю диалога из файла."""
    if os.path.exists(filename):
        with open(filename, "rb") as file:  # Открываем файл в бинарном режиме
            encrypted_data = file.read()
            decrypted_data = decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
    return []


def save_dialog_history(filename, dialog_history):
    """Шифрует и сохраняет историю диалога в файл."""
    encrypted_data = encrypt_data(
        json.dumps(dialog_history, ensure_ascii=False, indent=2))
    with open(filename, "wb") as file:
        file.write(encrypted_data)


def gpt(data):
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "x-data-logging-enabled": "false"
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise RuntimeError(
            f'Ошибка: код {response.status_code}, сообщение: {response.text}')

    response_json = response.json()
    try:
        return response_json["result"]["alternatives"][0]["message"]["text"]
    except (KeyError, IndexError):
        return "Ответ не найден"


def process_ai_response(user_id, chat_id=None, username=None,
                        user_message=None):
    filename = get_dialog_filename(user_id)
    dialog_history = load_dialog_history(filename)

    if not any(msg["role"] == "system" for msg in dialog_history):
        dialog_history.insert(0, {"role": "system", "text": WHO_IS_BOT})

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