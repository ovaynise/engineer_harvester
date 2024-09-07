import asyncio

from config import BOT_TOKEN, SUPER_USER_ID
from modules.ovay_bot import OvayBot
from handlers.user_private import user_private_router
from handlers.group_commands import group_commands_router
from handlers.api_handler import api_router
from handlers.group_and_private import group_and_private_router
from handlers.reminder_handler import reminder_router
from handlers.admin_handler import admin_router
from handlers.anonymous_group_and_private import anonymous_group_and_private_router
from handlers.super_user_handler import super_user_router
from inits.logger import bot_logger
from utils.security import add_super_user_on_bd
from config import TELEGRAM_GROUP_ID



def create_bot():
    ovay_bot = OvayBot(BOT_TOKEN, timeout=5, retry_attempts=3)
    ovay_bot.dp.include_router(user_private_router)
    ovay_bot.dp.include_router(api_router)
    ovay_bot.dp.include_router(reminder_router)
    ovay_bot.dp.include_router(admin_router)
    ovay_bot.dp.include_router(super_user_router)
    ovay_bot.dp.include_router(anonymous_group_and_private_router)
    ovay_bot.dp.include_router(group_and_private_router)
    ovay_bot.dp.include_router(group_commands_router)

    return ovay_bot


ovay_bot = create_bot()


async def main():
    await add_super_user_on_bd(SUPER_USER_ID)
    await ovay_bot.info_message(TELEGRAM_GROUP_ID, 'Бот начал работу!')
    bot_task = asyncio.create_task(ovay_bot.start())
    await asyncio.gather(bot_task)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        bot_logger.error(f'Ошибка {e}')
        raise
