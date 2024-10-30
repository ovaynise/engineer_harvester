from dotenv import load_dotenv
import os
from core.logger import OvayLogger
load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")
LOG_FILE_PATH = './logs'

logger_django = OvayLogger(
    name="logger_django",
    log_file_base_path=LOG_FILE_PATH).get_logger()