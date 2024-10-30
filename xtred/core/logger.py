import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os
import pytz


class OvayLogger:
    general_log_file_name = "logger_general.log"
    _general_handler = None

    def __init__(self, name, log_file_base_path):
        self.name = name
        self.log_file_base_path = log_file_base_path
        self.logger = logging.getLogger(name)
        self.setup_logging()

    def setup_logging(self):
        # Создаем путь к основному файлу лога
        log_file_path = os.path.join(self.log_file_base_path, f"{self.name}.log")
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        formatter = self.OvayFormatter(
            "[%(asctime)s - func:_%(filename)s.%(funcName)s - %(levelname)s]:\n"
            ">> %(message)s <<\n----"
        )
        self.logger.setLevel(logging.DEBUG)

        # Добавляем обработчик для основного файла
        handler = RotatingFileHandler(log_file_path, maxBytes=50000000, backupCount=5)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Если общий обработчик еще не создан, создаем его один раз
        if OvayLogger._general_handler is None:
            general_log_path = os.path.join(self.log_file_base_path, self.general_log_file_name)
            OvayLogger._general_handler = RotatingFileHandler(
                general_log_path, maxBytes=50000000, backupCount=5
            )
            OvayLogger._general_handler.setFormatter(formatter)

        # Добавляем общий обработчик к этому логгеру
        self.logger.addHandler(OvayLogger._general_handler)

    class OvayFormatter(logging.Formatter):
        def converter(self, timestamp):
            dt = datetime.fromtimestamp(timestamp)
            return dt.astimezone(pytz.timezone("Europe/Moscow"))

        def formatTime(self, record, datefmt=None):
            dt = self.converter(record.created)
            days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
            day_of_week = days[dt.weekday()]
            if datefmt:
                s = dt.strftime(datefmt)
            else:
                s = f"{day_of_week} {dt.strftime('%d.%m.%Y %H:%M:%S')}"
            return s

    def get_logger(self):
        return self.logger