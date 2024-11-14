from aiogram import Router, types
from aiogram.filters import Command
from config import logger_bot
from modules.ai_integration import process_ai_response
from config import TELEGRAM_GROUP_ID


group_and_private_router = Router()

def setup_group_and_private_handlers(ovay_bot):
    @group_and_private_router.message(Command(commands=["id"]))
    async def show_id(message: types.Message):
        logger_bot.debug("Отработала функция id")
        response_message = (f"Ваш id: {message.from_user.id}, "
                            f"id чата: {message.chat.id}, "
                            f"id темы: {message.message_thread_id}")
        await message.answer(response_message)
        await ovay_bot.info_message(
            chat_id=message.chat.id,
            bot_message=response_message,
            user_message=message.text,
            user_id=message.from_user.id,
            username=message.from_user.username or "Без имени",
            chat_title=message.chat.title if message.chat.title else message.from_user.username
        )

    @group_and_private_router.message()
    async def ai_response_handler(message: types.Message):
        user_message = message.text
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username or "Без имени"

        if message.chat.type in ["group", "supergroup"]:
            is_reply_to_bot = (
                    message.reply_to_message and message.reply_to_message.from_user.id == ovay_bot.bot.id)
            bot_mention = f"@{(await ovay_bot.bot.get_me()).username}"
            mentions_bot = (bot_mention in message.text) if message.text else False

            if not (is_reply_to_bot or mentions_bot):
                return
        bot_message = process_ai_response(user_id, chat_id, username, user_message)
        await message.answer(bot_message)
        await ovay_bot.info_message(
            chat_id=TELEGRAM_GROUP_ID,
            bot_message=bot_message,
            user_message=user_message,
            user_id=user_id,
            username=username,
            chat_title=message.chat.title if message.chat.title else username
        )

    return group_and_private_router