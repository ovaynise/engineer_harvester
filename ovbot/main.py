import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from config import (BOT_TOKEN, SUPER_USER_ID, TELEGRAM_GROUP_ID,
                    banwords_file_path, logger_bot)
from handlers.anonymous_group_and_private import \
    setup_anonymous_group_and_private_router_handlers
from handlers.api_handler import setup_api_router_handlers
from handlers.group_and_private import setup_group_and_private_handlers
from handlers.super_user_handler import setup_super_user_handlers
from middlewares.access_controle_middleware import AccessControlMiddleware
from middlewares.antiflood_middleware import AntiFloodMiddleware
from middlewares.forbidden_words_middleware import ForbiddenWordsMiddleware
from middlewares.ban_manager_middleware import BanManagerMiddleware
from middlewares.private_flood_middleware import PrivateFloodMiddleware
from modules.ovay_bot import OvayBot
from utils.security import add_super_user_on_bd


def create_dispatcher(ovay_bot: OvayBot) -> Dispatcher:
    dp = Dispatcher()

    # Подключение мидлваров
    dp.update.middleware(PrivateFloodMiddleware(ovay_bot))  # Личные сообщения
    dp.update.middleware(BanManagerMiddleware(ovay_bot))   # Общий бан
    dp.update.middleware(AccessControlMiddleware())        # Доступы
    dp.update.middleware(AntiFloodMiddleware(bot=ovay_bot))  # Флуд в группах
    dp.update.middleware(ForbiddenWordsMiddleware(bot=ovay_bot, banwords_file_path=banwords_file_path))

    # Регистрация хендлеров
    dp.include_router(setup_api_router_handlers(ovay_bot))
    dp.include_router(setup_super_user_handlers(ovay_bot))
    dp.include_router(setup_anonymous_group_and_private_router_handlers(ovay_bot))
    dp.include_router(setup_group_and_private_handlers(ovay_bot))

    return dp


async def main() -> None:
    dispatcher = Dispatcher()  # Создаём диспетчер
    ovay_bot = OvayBot(token=BOT_TOKEN, dp=dispatcher, timeout=5, retry_attempts=3)  # Передаём токен
    ovay_bot.dp = create_dispatcher(ovay_bot)  # Конфигурируем диспетчер
    await add_super_user_on_bd(SUPER_USER_ID)
    await ovay_bot.send_message(TELEGRAM_GROUP_ID, "Бот начал работу!!!")  # Используем ovay_bot для отправки сообщения
    bot_task = asyncio.create_task(ovay_bot.start())  # Запускаем бота
    await asyncio.gather(bot_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger_bot.error(f"Ошибка {e}")
        raise
