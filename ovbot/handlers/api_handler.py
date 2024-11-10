from aiogram import Router, types
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                security_filters)
from inits.cryptoshower import crypto_shower
from inits.weather_shower import weather_minsk

api_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel", "private"]),
    UserLevelFilter(0, 15, "IsAuthUser"),
]

def setup_api_router_handlers(ovay_bot):
    @security_filters(api_router, "temp", *common_filters)
    async def show_weather_minsk(message: types.Message):
        await message.answer(f"Погода в минске: {weather_minsk.info()},")


    @security_filters(api_router, "btc", *common_filters)
    async def show_btc(message: types.Message):
        await message.answer(f"Cтоимость биткоина: {crypto_shower.show_btc()},")

    return api_router
