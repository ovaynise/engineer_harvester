import os
import zipfile
from datetime import datetime

from aiogram import Router, types
from aiogram.types import InputFile
from config import LOG_FILE_PATH_SERVER, logger_bot
from filters.chat_types import (ChatTypesFilter, UserLevelFilter,
                                security_filters)


super_user_router = Router()
common_filters = [
    ChatTypesFilter(["group", "supergroup", "channel", "private"]),
    UserLevelFilter(0, 0, "IsSuperUser"),
]

def setup_super_user_handlers(ovay_bot):
    @security_filters(super_user_router, "logs", *common_filters)
    async def send_logs(message: types.Message):
        logger_bot.info("Команда /send_logs получена.")

        log_files = os.listdir(LOG_FILE_PATH_SERVER)
        logger_bot.info(f"Список файлов логов: {log_files}")

        if not log_files:
            await message.answer("Логи отсутствуют.")
            logger_bot.info("Логи отсутствуют.")
            return
        zip_filename = f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_file_path = os.path.join(LOG_FILE_PATH_SERVER, zip_filename)

        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            for filename in log_files:
                file_path = os.path.join(LOG_FILE_PATH_SERVER, filename)
                logger_bot.info(f"Обрабатываем файл: {file_path}")
                if filename == ".keep":
                    logger_bot.info(f"Пропускаем файл {filename}.")
                    continue

                if os.path.isfile(file_path):
                    logger_bot.info(f"{filename} - это файл.")
                    try:
                        file_size = os.path.getsize(file_path)
                        logger_bot.info(f"Размер файла {filename}: "
                                        f"{file_size} байт")

                        if file_size > 0:
                            zip_file.write(file_path, arcname=filename)

                            logger_bot.info(f"Файл {filename} добавлен в архив.")
                        else:
                            logger_bot.info(f"Файл {filename} пуст и не будет "
                                            f"добавлен в архив.")
                    except Exception as e:
                        logger_bot.info(f"Ошибка при добавлении {filename}"
                                        f" в архив: {str(e)}")
                        await message.answer(
                            f"Не удалось добавить лог файл {filename} "
                            f"в архив: {str(e)}"
                        )
                else:
                    logger_bot.info(f"{filename} - это не файл.")

        logger_bot.info(f"Отправляем архив {zip_filename}.")
        try:
            input_file = InputFile(zip_file_path)
            await message.answer_document(
                document=input_file,
                caption=f"Архив логов: {zip_filename}"
            )
            logger_bot.info(f"Архив {zip_filename} успешно отправлен.")
        except Exception as e:
            logger_bot.info(f"Ошибка при отправке архива {zip_filename}: {str(e)}")
            await message.answer(
                f"Не удалось отправить архив логов {zip_filename}: {str(e)}"
            )
        finally:
            os.remove(zip_file_path)


    @security_filters(super_user_router, "su", *common_filters)
    async def su_test(message: types.Message):
        await message.answer(
            f"SUPERUSER, подтвержен: {message.from_user.username}"
        )

    return super_user_router
