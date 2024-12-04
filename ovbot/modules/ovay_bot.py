import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramNetworkError
from config import TELEGRAM_GROUP_ID, logger_bot, logger_other


class OvayBot(Bot):  # Наследуемся от Bot
    def __init__(self, token: str, dp: Dispatcher, timeout=30, retry_attempts=3):
        super().__init__(token)  # Передаём токен в базовый класс
        self.dp = dp
        self.timeout = timeout
        self.retry_attempts = retry_attempts

    async def start(self):
        logger_bot.debug(f"Запуск бота {self}")
        for attempt in range(self.retry_attempts):
            try:
                await self.delete_webhook(drop_pending_updates=True)
                logger_bot.debug("Webhook удален.")
                commands = [
                    types.BotCommand(command="/start",
                                     description="Start the bot"),
                    types.BotCommand(command="/help",
                                     description="Get help"),
                ]
                await self.set_my_commands(
                    commands=commands,
                    scope=types.BotCommandScopeAllPrivateChats())

                await self.dp.start_polling(self,
                                            timeout=self.timeout)
                logger_bot.debug("Запущен процесс polling")
                break
            except TelegramNetworkError as e:
                logger_bot.error(f"Ошибка сети: {e}. Повторная попытка... "
                                 f"(попытка {attempt + 1})")
                await asyncio.sleep(5)
            except Exception as e:
                logger_bot.error(f"Необработанная ошибка: {e}")
                await asyncio.sleep(5)
        else:
            logger_bot.error(f"Не удалось запустить "
                             f"бота после {self.retry_attempts} попыток.")
        await self.session.close()

    async def info_message(self, chat_id, bot_message, user_message=None,
                           user_id=None, username=None, chat_title=None):
        try:
            if user_message is not None and user_id is not None:
                log_text = (
                    f"🟧User: @{username} (ID: {user_id}, Chat: '{chat_title}', Chat ID: {chat_id}) "
                    f"\nsent message:▶️ {user_message} ◀️🟧"
                )
                logger_other.info(log_text)
                await self.send_message(TELEGRAM_GROUP_ID, log_text)
            bot_log_text = (
                f'🟩▶️Bot sent message "{bot_message}" to chat "{chat_title}" (Chat ID: {chat_id})◀️🟩'
            )
            logger_other.info(bot_log_text)
        except Exception as e:
            logger_bot.error(f"Error sending message: {e}")