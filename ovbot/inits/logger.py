from config import log_file_path, log_file_path2, log_file_path3
from modules.ovay_logger import OvayLogger

bot_logger = OvayLogger(
    name="bot_logger", log_file_path=log_file_path
).get_logger()
db_logger = OvayLogger(
    name="db_logger", log_file_path=log_file_path2
).get_logger()
other_logger = OvayLogger(
    name="other_logger", log_file_path=log_file_path3
).get_logger()
