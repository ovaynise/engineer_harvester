import os

from dotenv import find_dotenv, load_dotenv
from modules.ovay_logger import OvayLogger

load_dotenv(find_dotenv())

TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID"))
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")

CMC_API_KEY = os.getenv("CMC_API_KEY")
crypto_url = os.getenv("CRYPTO_URL")
URL_SERVER_API = os.getenv("URL_SERVER_API")
API_WEATHER_KEY = os.getenv("WEATHER_API_key")
SUPER_USER_ID = os.getenv("SUPER_USER_ID")

YANDEX_OAUTH_TOKEN = os.getenv("YANDEX_OAUTH_TOKEN")
YCLOUD_CATALOG_ID = os.getenv("YCLOUD_CATALOG_ID")
API_KEY = os.getenv("API_KEY")
IAM_TOKEN = os.getenv("IAM_TOKEN")
banwords_file_path = 'utils/banwords.json'

WHO_IS_BOT = ('Умный но ворчливый ассистент по имени Джарвис'
              'отвечает постоянно с сарказмом ')


LOG_FILE_PATH_SERVER = "/app/logs"
LOG_FILE_PATH = "./logs"
DIALOGS_DIR_SERVER = "/app/dialogs"
DIALOGS_DIR = "./dialogs"
SALT = os.getenv("SALT")

logger_bot = OvayLogger(
    name="logger_bot",
    log_file_base_path=LOG_FILE_PATH).get_logger()

logger_db = OvayLogger(
    name="logger_db",
    log_file_base_path=LOG_FILE_PATH).get_logger()
logger_other = OvayLogger(
    name="logger_other",
    log_file_base_path=LOG_FILE_PATH).get_logger()

endpoint_reminder = "reminders/"
endpoint_entity = "entity/"
endpoint_constructions = "constructions/"
endpoint_users = "users/"
endpoint_constructions_works = "constructions-works/"
endpoint_constructions_company = "constructions-company/"
endpoint_location = "location/"
endpoint_brand_type = "brand-type/"
endpoint_tg_users = "tg-users/"
endpoint_banlist = "banlist/"

headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

LEVEL_RANGS = {
    0: "SUPER_USER",
    1: "ZAM_SUPER_USER",
    2: "LEADER",
    3: "ZAM_LEADER",
    4: "ADMIN_CHANEL",
    5: "MANAGER",
    6: "WORKER_TEAM",
    7: "WORKER_COMPANY",
    (8, 9, 10, 11, 12, 13, 14): "ANOTHER",
    15: "AUTH_USER",
    16: "ANONYM_USER",
}


crypto_parameters = {"start": "1", "limit": "5000", "convert": "USD"}
crypto_headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": CMC_API_KEY,
}

CITIES = {
    "Минск": [53.842316, 27.695950],
}
