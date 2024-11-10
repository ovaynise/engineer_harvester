import asyncio

from config import BOT_TOKEN, SUPER_USER_ID, TELEGRAM_GROUP_ID, logger_bot
from handlers.admin_handler import setup_admin_handlers
from handlers.anonymous_group_and_private import \
    setup_anonymous_group_and_private_router_handlers
from handlers.api_handler import setup_api_router_handlers
from handlers.group_and_private import setup_group_and_private_handlers
from handlers.group_commands import setup_group_commands_handlers
from handlers.super_user_handler import setup_super_user_handlers
from handlers.user_private import setup_user_private_handlers
from modules.ovay_bot import OvayBot
from utils.security import add_super_user_on_bd


def create_bot() -> OvayBot:
    ovay_bot = OvayBot(BOT_TOKEN, timeout=5, retry_attempts=3)
    ovay_bot.dp.include_router(setup_user_private_handlers(ovay_bot))
    ovay_bot.dp.include_router(setup_api_router_handlers(ovay_bot))
    ovay_bot.dp.include_router(setup_admin_handlers(ovay_bot))
    ovay_bot.dp.include_router(setup_super_user_handlers(ovay_bot))
    ovay_bot.dp.include_router(
        setup_anonymous_group_and_private_router_handlers(ovay_bot))
    ovay_bot.dp.include_router(setup_group_and_private_handlers(ovay_bot))
    ovay_bot.dp.include_router(setup_group_commands_handlers(ovay_bot))
    return ovay_bot


async def main() -> None:
    ovay_bot = create_bot()
    await add_super_user_on_bd(SUPER_USER_ID)
    await ovay_bot.info_message(TELEGRAM_GROUP_ID,
                                "Бот начал работу!!!")
    bot_task = asyncio.create_task(ovay_bot.start())
    await asyncio.gather(bot_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger_bot.error(f"Ошибка {e}")
        raise
