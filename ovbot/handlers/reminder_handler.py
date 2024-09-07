from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import endpoint_reminder
from filters.chat_types import ChatTypesFilter, UserLevelFilter
from inits.api_client import api_ov_client
from inits.logger import bot_logger
from keyboards.kb_reply import get_keyboard
from utils.reminder_func import days_or_months, extract_time_intervals
from utils.security import crypt
from utils.states import ReminderForm
from utils.user_utils import get_user_level

reminder_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel", "private"]),
    UserLevelFilter(0, 15, "IsAuthUser"),
]


REMINDER_KB = get_keyboard(
    "▶️ Запустить напоминание",
    "⏸ Остановить напоминание",
    "▪ Создать напоминание",
    "▪ Показать все Ваши напоминания",
    "🗑 Удалить напоминание",
    "⭕️ Выход",
    placeholder="Выберите действие",
    sizes=(2, 2, 2),
)


async def check_user_level(
    message: types.Message, required_min: int, required_max: int
) -> bool:
    user_id = message.from_user.id
    user_level = await get_user_level(crypt(user_id))
    if user_level is None or not (required_min <= user_level <= required_max):
        await message.answer(
            f"Для выполнения команды "
            f"требуется уровень доступа от {required_min} до {required_max}. "
            f"Ваш уровень: {user_level}."
        )
        return False
    return True


EXIT_KB = get_keyboard(
    "⭕️ Выход",
    sizes=(2, 1, 1),
)


@reminder_router.message(F.text == "⭕️ Выход")
async def exit_keyboard(message: types.Message, state: FSMContext):
    await message.answer(
        "Вы вышли из меню.", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()


@reminder_router.message(Command("reminder"))
async def get_bat(message: types.Message, bot: Bot):
    if not await check_user_level(message, 0, 15):
        await bot.send_message(
            message.from_user.id,
            "У вас не достаточный уровень для создания напоминания",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    chat_type = message.chat.type
    await message.delete()

    if message.text in [
        "▪ Создать напоминание",
        "▪ Показать все Ваши напоминания",
        "🗑 Удалить напоминание",
    ]:
        await bot.send_message(
            message.from_user.id,
            "Что Вы хотите выполнить?",
            reply_markup=REMINDER_KB,
        )
        bot_logger.info("🔢Запущено создание напоминания")
    elif message.text in [
        "▶️ Запустить напоминание",
        "⏸ Остановить напоминание",
    ]:
        await bot.send_message(
            message.from_user.id,
            "Приступим к выполнению:",
            reply_markup=REMINDER_KB,
        )
        bot_logger.info("🔢Запущено выполнение напоминания")
    elif chat_type in ["group", "supergroup"]:
        await bot.send_chat_action(message.chat.id, "typing")
        await bot.send_message(
            message.from_user.id,
            "Приступим к созданию:",
            reply_markup=REMINDER_KB,
        )
        bot_logger.info("🔢Запущено создание напоминания в групповом чате")
    else:
        await bot.send_message(
            message.from_user.id,
            "Что Вы хотите выполнить?",
            reply_markup=REMINDER_KB,
        )
        bot_logger.info("🔢Запущено создание напоминания в личном чате")


@reminder_router.message(F.text == "▪ Создать напоминание")
async def add_reminder(message: types.Message, state: FSMContext):
    if not await check_user_level(message, 0, 15):
        await state.clear()  # Завершаем машину состояний
        return
    await add_name_reminder(message, state)
    await message.answer("___________", reply_markup=EXIT_KB)


async def add_name_reminder(message: types.Message, state: FSMContext):
    await state.set_state(ReminderForm.name_reminder)
    await message.answer("Введите название напоминания:")


@reminder_router.message(ReminderForm.name_reminder)
async def add_text_reminder(message: types.Message, state: FSMContext):
    await state.update_data(name_reminder=message.text)
    await state.set_state(ReminderForm.text_reminder)
    await message.answer("Введите текст напоминания:")


@reminder_router.message(ReminderForm.text_reminder)
async def add_reminder_repeat(message: types.Message, state: FSMContext):
    await state.update_data(text_reminder=message.text)
    await state.set_state(ReminderForm.reminder_days)
    await choose_days(message, state)


@reminder_router.message(ReminderForm.reminder_days)
async def choose_days(message: types.Message, state: FSMContext):
    await message.answer(
        "Напишите день (пн,вт,ср,чт,пт,сб,вс), "
        "когда вам напомнить или число месяца: ",
        reply_markup=EXIT_KB,
    )
    await state.set_state(ReminderForm.choose_time)


@reminder_router.message(ReminderForm.choose_time)
async def choose_time(message: types.Message, state: FSMContext):
    reminder_day = message.text
    days, month_day = days_or_months(reminder_day)
    await state.update_data(days=days)
    await state.update_data(month_day=month_day)
    await state.set_state(ReminderForm.add_db_reminder_time)
    await message.answer(
        "Напишите время напоминания в формате: 10-12 или 12:00",
        reply_markup=EXIT_KB,
    )


@reminder_router.message(ReminderForm.add_db_reminder_time)
async def add_db_reminder_time(message: types.Message, state: FSMContext):
    await state.set_state(ReminderForm.choose_time)
    await state.update_data(choose_time=message.text)
    try:
        data = await state.get_data()

        api_data = {
            "reminder_nickname": "",
            "name_reminder": "",
            "text_reminder": "",
            "days_repeat": {
                "days_week": [],
                "month_days": [],
                "time_repeat": [],
            },
            "owner_reminder_id": "",
        }

        nickname = (
            str(message.from_user.first_name)
            + " "
            + str(message.from_user.last_name)
        )
        api_data["reminder_nickname"] = data.get("name_reminder", "не указано")
        api_data["name_reminder"] = data.get(
            "name_reminder", "текст не указали"
        )
        api_data["text_reminder"] = data.get(
            "text_reminder", "текст не указали"
        )
        api_data["days_repeat"]["month_days"] = data.get("month_day", [])
        api_data["days_repeat"]["days_week"] = data.get("days", [])
        api_data["days_repeat"]["time_repeat"] = extract_time_intervals(
            data.get("choose_time", [])
        )
        api_data["owner_reminder_id"] = crypt(message.from_user.id)
        api_data["reminder_nickname"] = nickname
        reminder = await api_ov_client.post(endpoint_reminder, api_data)
        today = datetime.utcnow()
        await message.answer(
            "Напоминание успешно создано", reply_markup=REMINDER_KB
        )
        await state.clear()
        await message.answer(
            f'Вы создали напоминание №{reminder.get("id")}:\n'
            f'Название: {api_data["name_reminder"]}\n'
            f'Текст: {api_data["text_reminder"]}\n'
            f"Время создания: {today}\n"
            f"Создатель: "
            f'{reminder.get("reminder_nickname", "не указано")}'
            f"___________"
        )

    except ValueError as e:
        await message.answer(
            f"Ошибка: {e}. "
            f"Пожалуйста, укажите корректное "
            f"время напоминания."
        )
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении объекта: {e}")


@reminder_router.message(F.text == "▪ Показать все Ваши напоминания")
async def show_reminders(message: types.Message, bot: Bot):
    if not await check_user_level(message, 0, 15):
        await bot.send_message(
            message.from_user.id,
            "У вас не достаточный уровень для создания напоминания",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return
    await message.delete()
    try:
        reminders_response = await api_ov_client.get(
            f"{endpoint_reminder}?owner_reminder_id="
            f"{crypt(message.from_user.id)}"
        )
        if reminders_response and reminders_response.get("results"):
            reminders = reminders_response["results"]
            bot_message = "⬇️Список всех ваших напоминаний:⬇️\n\n"
            for reminder in reminders:
                chats = reminder.get("chats_names_active", [])
                if chats:
                    chats_str = ", ".join(chats)
                    status = "🟢"
                else:
                    chats_str = " Нет активных чатов"
                    status = "🔴"

                bot_message += (
                    f'№{reminder.get("id")}:{reminder.get("name_reminder")} \n'
                    f"Чаты:{status} \n"
                    f"{chats_str}\n"
                    f"〰️〰️〰️〰️〰️〰️〰️\n"
                )
            await bot.send_message(message.from_user.id, bot_message)
        else:
            await bot.send_message(
                message.from_user.id, "😱У вас нет созданных напоминаний."
            )
    except Exception as e:
        await bot.send_message(message.from_user.id, f"Произошла ошибка: {e}")


@reminder_router.message(F.text == "🗑 Удалить напоминание")
async def delete_reminder_command(message: types.Message, state: FSMContext):
    if not await check_user_level(message, 0, 15):
        await state.clear()
        return
    await state.set_state(ReminderForm.delete_reminder_id)
    await message.answer("Введите ID напоминания, которое нужно удалить:")


@reminder_router.message(ReminderForm.delete_reminder_id)
async def handle_delete_reminder_id(message: types.Message, state: FSMContext):
    try:
        reminder_id = int(message.text)
        reminder = await api_ov_client.get(
            f"{endpoint_reminder}{reminder_id}/"
        )
        if reminder["owner_reminder_id"] == crypt(message.from_user.id):
            await api_ov_client.delete(endpoint_reminder, reminder_id)
            await message.answer(
                f"Напоминание с ID {reminder_id} успешно " f"удалено.",
                reply_markup=types.ReplyKeyboardRemove(),
            )
            await state.clear()
        else:
            await message.answer(
                "Вы не являетесь владельцем этого"
                " напоминания и не можете его "
                "удалить.",
                reply_markup=EXIT_KB,
            )
    except ValueError:
        await message.answer(
            "Вы ввели не число или не "
            "ваше напоминание. Повторите попытку "
            "или нажмите Выход",
            reply_markup=EXIT_KB,
        )
    except Exception as e:
        await message.answer(
            f"Произошла " f"ошибка: {e}", reply_markup=EXIT_KB
        )


@reminder_router.message(F.text == "▶️ Запустить напоминание")
async def start_reminder_command(message: types.Message, state: FSMContext):
    if not await check_user_level(message, 0, 15):
        await state.clear()
        return
    await state.set_state(ReminderForm.start_reminder_id)
    await message.answer("▶️ Введите ID напоминания, которое нужно запустить:")


@reminder_router.message(ReminderForm.start_reminder_id)
async def handle_start_reminder_id(message: types.Message, state: FSMContext):
    try:
        reminder_id = int(message.text)
        reminder = await api_ov_client.get(
            f"{endpoint_reminder}{reminder_id}/"
        )
        if reminder["owner_reminder_id"] == crypt(message.from_user.id):
            chat_id = (
                crypt(message.chat.id) + "_" + str(message.message_thread_id)
            )
            chat_name = (
                message.chat.title
                if (message.chat.title)
                else f"{message.from_user.first_name}"
            )

            api_data = {
                "chats_id_active": reminder.get("chats_id_active", [])
                + [chat_id],
                "status_reminder": True,
                "chats_names_active": reminder.get("chats_names_active", [])
                + [chat_name],
            }
            await api_ov_client.patch(endpoint_reminder, api_data, reminder_id)

            await message.answer(
                f"▶️ Напоминание с "
                f"ID {reminder_id} успешно запущено "
                f"в чате {chat_name}."
            )
            await state.clear()
        else:
            await message.answer(
                "Вы не являетесь владельцем "
                "этого напоминания и не "
                "можете его запустить."
            )
    except ValueError:
        await message.answer(
            "Вы ввели не число. " "Повторите попытку.", reply_markup=EXIT_KB
        )
    except Exception as e:
        await message.answer(
            f"Произошла " f"ошибка: {e}", reply_markup=EXIT_KB
        )


@reminder_router.message(F.text == "⏸ Остановить напоминание")
async def stop_reminder_command(message: types.Message, state: FSMContext):
    if not await check_user_level(message, 0, 15):
        await state.clear()
        return
    await state.set_state(ReminderForm.stop_reminder_id)
    await message.answer("⏸ Введите ID напоминания, которое нужно остановить:")


@reminder_router.message(ReminderForm.stop_reminder_id)
async def handle_stop_reminder_id(message: types.Message, state: FSMContext):
    try:
        reminder_id = int(message.text)
        chat_id = str(message.chat.id) + "_" + str(message.message_thread_id)
        reminder = await api_ov_client.get(
            f"{endpoint_reminder}{reminder_id}/"
        )
        if reminder["owner_reminder_id"] == crypt(message.from_user.id):
            chats_id_active = reminder.get("chats_id_active", [])
            chats_names_active = reminder.get("chats_names_active", [])
            if chat_id in chats_id_active:
                chats_id_active.remove(chat_id)
            chat_name = (
                message.chat.title
                if (message.chat.title)
                else f"{message.from_user.first_name}"
            )
            if chat_name in chats_names_active:
                chats_names_active.remove(chat_name)
            api_data = {
                "chats_id_active": chats_id_active,
                "status_reminder": len(chats_id_active) > 0,
                "chats_names_active": chats_names_active,
            }
            await api_ov_client.patch(endpoint_reminder, api_data, reminder_id)
            await message.answer(
                f"⏸ Напоминание с"
                f" ID {reminder_id} успешно"
                f" остановлено в этом чате."
            )
            await state.clear()
        else:
            await message.answer(
                "Вы не являетесь владельцем "
                "этого напоминания и не "
                "можете его остановить."
            )
    except ValueError:
        await message.answer(
            "Вы ввели не число. " "Повторите попытку.", reply_markup=EXIT_KB
        )
    except Exception as e:
        await message.answer(
            f"Произошла " f"ошибка: {e}", reply_markup=EXIT_KB
        )
