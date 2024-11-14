from aiogram import Router, types
from aiogram.filters import Command
from config import logger_bot, TELEGRAM_GROUP_ID
from modules.ai_integration import process_ai_response
from aiogram.types import ChatPermissions, ChatMemberOwner, ChatMemberAdministrator
from datetime import datetime, timedelta
from utils.user_utils import get_user_level
from utils.security import crypt

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

        target_username = args[0]

        # Проверка прав суперпользователя
        user_level = await get_user_level(crypt(message.from_user.id))
        if user_level != SUPER_USER_LEVEL:
            await message.reply(
                "У вас недостаточно прав для использования этой команды.")
            return

        # Получаем информацию о целевом пользователе
        try:
            target_user = await ovay_bot.bot.get_chat_member(
                message.chat.id,
                target_username.replace('@', '')
            )
        except:
            await message.reply(f"Пользователь {target_username} не найден.")
            return

        # Снимаем ограничения с пользователя в групповом чате
        await ovay_bot.bot.restrict_chat_member(
            message.chat.id,
            target_user.user.id,
            permissions=ChatPermissions(can_send_messages=True)
        )

        # Снимаем ограничения с пользователя в личной переписке, если таковая есть
        try:
            await ovay_bot.bot.restrict_chat_member(
                target_user.user.id,  # Личный чат с пользователем
                target_user.user.id,
                permissions=ChatPermissions(can_send_messages=True)
            )
        except Exception as e:
            await message.reply(
                f"Не удалось разблокировать пользователя в личной переписке: {e}")

        await message.reply(f"Пользователь {target_username} разблокирован.")

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