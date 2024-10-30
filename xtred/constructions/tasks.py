import datetime
import time

import httpx
from celery import shared_task
from config import BOT_TOKEN, TELEGRAM_GROUP_ID

now = datetime.datetime.now()
formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")


@shared_task
def hello():
    return 'test task'


@shared_task()
def bot_send_message(retries=3):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_GROUP_ID,
        'text': f'Тестовая отправка через celery,'
                f' текущее время: {formatted_now}'}

    for attempt in range(retries):
        try:
            response = httpx.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return
        except httpx.RequestError:
            if attempt < retries - 1:
                time.sleep(2)
