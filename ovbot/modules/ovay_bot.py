import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramNetworkError
from config import logger_bot, TELEGRAM_GROUP_ID


class OvayBot:
    def __init__(self, token, timeout=30, retry_attempts=3):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.timeout = timeout
        self.retry_attempts = retry_attempts

    async def start(self):
        bot = self.bot
        logger_bot.debug(f"Создан объект бота {bot}")
        dp = self.dp
        logger_bot.debug(f"Создан объект диспетчера {dp}")
        for attempt in range(self.retry_attempts):
            try:
                await bot.delete_webhook(drop_pending_updates=True)
                logger_bot.debug("Webhook deleted.")

                commands = [
                    types.BotCommand(
                        command="/start", description="Start the bot"
                    ),
                    types.BotCommand(command="/help", description="Get help"),
                ]

                await bot.set_my_commands(
                    commands=commands,
                    scope=types.BotCommandScopeAllPrivateChats(),
                )
                await dp.start_polling(bot, timeout=self.timeout)
                logger_bot.debug("Запущен процесс polling")
                break
            except TelegramNetworkError as e:
                logger_bot.error(
                    f"Ошибка сети: {e}. Повторная "
                    f"попытка... (попытка {attempt + 1})"
                )
                await asyncio.sleep(5)
            except Exception as e:
                logger_bot.error(f"Необработанная ошибка: {e}")
                await asyncio.sleep(5)
        else:
            logger_bot.error(
                f"Не удалось запустить бота "
                f"после {self.retry_attempts} попыток."
            )
        await self.bot.session.close()

    def run(self):
        asyncio.run(self.start())
        logger_bot.debug("Запущена функция run бота на asyncio")

    async def info_message(self, chat_id, bot_message, user_message=None,
                           user_id=None, username=None, chat_title=None):
        try:
            if user_message is not None and user_id is not None:
                log_text = (
                    f" 🟧▶️User: @{username} (ID: {user_id}, Chat: '{chat_title}', Chat ID: {chat_id}) "
                    f"sent message: {user_message} ◀️🟧"
                )
                logger_bot.info(log_text)
                await self.bot.send_message(TELEGRAM_GROUP_ID, log_text)

            await self.bot.send_message(chat_id, bot_message)
            bot_log_text = f'🟩▶️Bot sent message "{bot_message}" to chat "{chat_title}" (Chat ID: {chat_id})◀️🟩'
            logger_bot.debug(bot_log_text)
            await self.bot.send_message(TELEGRAM_GROUP_ID, bot_log_text)

        except Exception as e:
            logger_bot.error(f"Error sending message: {e}")
