import hashlib
import hmac
import os
import time

from django.http import HttpResponse
from django.shortcuts import render
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# Получите токен вашего бота
BOT_TOKEN = os.getenv("BOT_TOKEN")


def telegram_auth(request):
    # Получаем параметры из запроса
    id = request.GET.get('id')
    first_name = request.GET.get('first_name')
    last_name = request.GET.get('last_name')
    username = request.GET.get('username')
    photo_url = request.GET.get('photo_url')
    auth_date = request.GET.get('auth_date')
    received_hash = request.GET.get('hash')

    # Собираем строку для проверки (data-check-string)
    data_check_string = (f"auth_date={auth_date}"
                         f"\nfirst_name={first_name}\nid={id}"
                         f"\nusername={username}")

    # Вычисляем секретный ключ как SHA256 от токена бота
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()

    # Проверяем HMAC-SHA256 подпись
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256).hexdigest()

    if calculated_hash == received_hash:
        # Проверяем, что данные не устарели
        if time.time() - int(auth_date) < 86400:  # 86400 секунд = 24 часа
            # Данные подлинные и не устарели, передаем их в шаблон
            context = {
                'id': id,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'photo_url': photo_url,
            }
            return render(request, 'auth_success.html', context)
        else:
            return HttpResponse("Data expired")
    else:
        return HttpResponse("Invalid data")
