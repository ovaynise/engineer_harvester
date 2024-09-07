import hashlib
import os
from dotenv import find_dotenv, load_dotenv

from inits.api_client import api_ov_client
from config import endpoint_tg_users
from inits.logger import db_logger

load_dotenv(find_dotenv())


def crypt(text, SALT = os.getenv('SALT')):
    text = str(text)
    text_bytes = text.encode('utf-8')
    salt_bytes = SALT.encode('utf-8')
    sha256 = hashlib.sha256()
    sha256.update(text_bytes + salt_bytes)
    return sha256.hexdigest()


async def add_super_user_on_bd(user_hash_id):
    try:
        user_response = await api_ov_client.get(f"{endpoint_tg_users}?tg_user_id={user_hash_id}")
        if user_response['count'] > 0:
            user_in_bd = user_response['results'][0]['tg_user_id']
            if user_hash_id == user_in_bd:
                db_logger.debug(f'Супер Пользователь успешно найден в БД')
                return
        api_data = {
            'tg_user_id': user_hash_id,
            'tg_first_name': 'super_user',
            'tg_last_name': 'super_user',
            'tg_user_name': 'super_user',
            'ban_status': False,
            'level': 0
        }
        await api_ov_client.post(endpoint_tg_users, api_data)
        db_logger.debug(f'Супер Пользователь! Успешно зарегистрирован!')
    except ValueError:
        db_logger.error('Произошла ошибка при обработке ID пользователя.')
    except KeyError:
        db_logger.error('Произошла ошибка при доступе к данным пользователя.')
    except Exception as e:
        db_logger.error(f'Произошла ошибка: {e}')
