from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from utils.security import crypt
from utils.user_utils import get_user_level

INITIAL_BLOCK_DURATION = 1
SECOND_BLOCK_DURATION = 5
SUBSEQUENT_BLOCK_DURATION = 30



class AccessControlMiddleware(BaseMiddleware):
    def __init__(self, min_level: int = 0, max_level: int = 15):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    async def __call__(self, handler, event: Update, data: dict):
        if (isinstance(event,
                       Update) and event.message and isinstance(event.message,
                                                                Message)):
            message = event.message
            user_id = message.from_user.id
            if (message.text.startswith("/status") or message.text.startswith(
                    "/start")):
                return await handler(event, data)
            user_level = await get_user_level(crypt(user_id))

            if user_level is None:
                await message.answer("Для доступа необходимо"
                                     " зарегистрироваться. Введите "
                                     "/start для регистрации.")
                return

            elif not (self.min_level <= user_level <= self.max_level):
                await message.answer(
                    f"Недостаточно прав. Ваш уровень: {user_level}."
                    f" Необходимо от {self.min_level} до {self.max_level}. "
                    f"Введите команду /start для регистрации."
                )
                return
        return await handler(event, data)
