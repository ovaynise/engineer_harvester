import logging
from datetime import datetime
import pytz
from logging.handlers import RotatingFileHandler


class OvayLogger:
    def __init__(self, name, log_file_path):
        self.logger = logging.getLogger(name)
        self.log_file_path = log_file_path
        self.setup_logging()

    def setup_logging(self):
        formatter = self.OvayFormatter(
            '[%(asctime)s - func:_%(filename)s.%(funcName)s- %(levelname)s ]:'
            '\n >> %(message)s <<\n ----'
        )
        self.logger.setLevel(logging.DEBUG)
        handler = ReversedRotatingFileHandler(
            self.log_file_path,
            maxBytes=50000000,
            backupCount=5
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    class OvayFormatter(logging.Formatter):
        def converter(self, timestamp):
            dt = datetime.fromtimestamp(timestamp)
            return dt.astimezone(pytz.timezone('Europe/Moscow'))

        def formatTime(self, record, datefmt=None):
            dt = self.converter(record.created)
            days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
            day_of_week = days[dt.weekday()]
            if datefmt:
                s = dt.strftime(datefmt)
            else:
                s = f"{day_of_week} {dt.strftime('%d.%m.%Y %H:%M:%S')}"
            return s

    def get_logger(self):
        return self.logger


class ReversedRotatingFileHandler(RotatingFileHandler):
    def emit(self, record):
        try:
            if self.shouldRollover(record):
                self.doRollover()
            log_entry = self.format(record)
            with open(self.baseFilename, 'r+') as file:
                content = file.read()
                file.seek(0, 0)
                file.write(log_entry + '\n' + content)
        except Exception:
            self.handleError(record)
