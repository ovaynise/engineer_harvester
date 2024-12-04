from aiogram import Router, types
from aiogram.filters import Command
from config import logger_bot, TELEGRAM_GROUP_ID
from modules.ai_integration import process_ai_response
from aiogram.types import ChatPermissions, ChatMemberOwner, ChatMemberAdministrator
from datetime import datetime, timedelta
from utils.user_utils import get_user_level
from utils.security import crypt
from middlewares.user_block_manager import reset_warnings, blocked_users

group_and_private_router = Router()

def setup_group_and_private_handlers(ovay_bot):
    SUPER_USER_LEVEL = 0
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

    @group_and_private_router.message(Command(commands=["ban"]))
    async def ban_user(message: types.Message):
        args = message.text.split()[1:]
        if len(args) != 2:
            await message.reply("Используйте: /ban @username <минуты>")
            return

        target_username, duration_str = args

        try:
            duration = int(duration_str)
        except ValueError:
            await message.reply("Неверный формат времени блокировки.")
            return

        user_level = await get_user_level(crypt(message.from_user.id))
        if user_level != SUPER_USER_LEVEL:
            await message.reply(
                "У вас недостаточно прав для использования этой команды.")
            return

        try:
            target_user = await ovay_bot.bot.get_chat_member(
                message.chat.id,
                target_username.replace('@', '')
            )
        except:
            await message.reply(f"Пользователь {target_username} не найден.")
            return

        if isinstance(target_user, (ChatMemberOwner, ChatMemberAdministrator)):
            await message.reply(
                "Вы не можете заблокировать администратора или владельца чата.")
            return

        block_until = datetime.now() + timedelta(minutes=duration)

        await ovay_bot.bot.restrict_chat_member(
            message.chat.id,
            target_user.user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=block_until
        )

    @group_and_private_router.message(Command(commands=["unban"]))
    async def unban_user(message: types.Message):
        args = message.text.split()[
               1:]  # Получаем аргументы команды после '/unban'
        if len(args) != 1:
            await message.reply("Используйте: /unban @username")
            return

        target_username = args[0].lstrip("@")  # Убираем '@', если оно есть

        # Проверка прав суперпользователя
        user_level = await get_user_level(crypt(message.from_user.id))
        if user_level != SUPER_USER_LEVEL:
            await message.reply(
                "У вас недостаточно прав для использования этой команды.")
            return

        # Получаем ID пользователя по username
        try:
            target_user = await ovay_bot.get_chat(target_username)
            target_user_id = target_user.id
        except Exception as e:
            await message.reply(
                f"Пользователь @{target_username} не найден. Ошибка: {e}")
            return

        # Снимаем ограничения в Telegram (групповой чат)
        try:
            await ovay_bot.restrict_chat_member(
                message.chat.id,
                target_user_id,
                permissions=ChatPermissions(can_send_messages=True)
            )
            logger_bot.info(
                f"Ограничения для пользователя {target_user_id} сняты в чате {message.chat.id}.")
        except Exception as e:
            await message.reply(f"Не удалось снять ограничения в чате: {e}")
            return

        # Полностью удаляем пользователя из всех блокировочных структур
        if message.chat.id in blocked_users and target_user_id in \
                blocked_users[message.chat.id]:
            del blocked_users[message.chat.id][target_user_id]
            logger_bot.info(
                f"Пользователь {target_user_id} удалён из blocked_users в чате {message.chat.id}.")

        # Сбрасываем предупреждения для пользователя
        reset_warnings(message.chat.id, target_user_id)
        logger_bot.info(
            f"Предупреждения пользователя {target_user_id} сброшены в чате {message.chat.id}.")


        await message.reply(
            f"Пользователь @{target_username} успешно разбанен.")

    @group_and_private_router.message()
    async def ai_response_handler(message: types.Message):
        user_message = message.text
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username or "Без имени"

        if message.chat.type in ["group", "supergroup"]:
            is_reply_to_bot = (
                    message.reply_to_message and message.reply_to_message.from_user.id == ovay_bot.id)
            bot_mention = f"@{(await ovay_bot.get_me()).username}"
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