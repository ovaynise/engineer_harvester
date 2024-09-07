from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())

TELEGRAM_GROUP_ID = int(os.getenv('TELEGRAM_GROUP_ID'))
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
BOT_TOKEN = os.getenv('BOT_TOKEN')

CMC_API_KEY = os.getenv('CMC_API_KEY')
crypto_url = os.getenv('CRYPTO_URL')
URL_SERVER_API = os.getenv('URL_SERVER_API')
URL_SERVER_API_DOCKER = os.getenv('URL_SERVER_API_DOCKER')
log_file_path = os.getenv('BOT_LOG_FILE_PATH', '/app/logs/bot_log.log')
log_file_path2 = os.getenv('DB_LOG_FILE_PATH', '/app/logs/db_log.log')
log_file_path3 = os.getenv('OTHER_LOG_FILE_PATH', '/app/logs/other_log.log')
API_WEATHER_KEY = os.getenv('WEATHER_API_key')
SUPER_USER_ID = os.getenv('SUPER_USER_ID')
AI_API_KEY = os.getenv('AI_API_KEY')
AI_URL_API = os.getenv('AI_URL_API')
AI_BALANCE_URL = os.getenv('AI_BALANCE_URL')
SALT = os.getenv("SALT")

endpoint_reminder = 'reminders/'
endpoint_entity = 'entity/'
endpoint_constructions = 'constructions/'
endpoint_users = 'users/'
endpoint_constructions_works = 'constructions-works/'
endpoint_constructions_company = 'constructions-company/'
endpoint_location = 'location/'
endpoint_brand_type = 'brand-type/'
endpoint_tg_users = 'tg-users/'
endpoint_banlist = 'banlist/'

headers = {
    'Authorization': f'Bearer {BEARER_TOKEN}'
}

LEVEL_RANGS = {
    0: 'SUPER_USER',
    1: 'ZAM_SUPER_USER',
    2: 'LEADER',
    3: 'ZAM_LEADER',
    4: 'ADMIN_CHANEL',
    5: 'MANAGER',
    6: 'WORKER_TEAM',
    7: 'WORKER_COMPANY',
    (8, 9, 10, 11, 12, 13, 14): 'ANOTHER',
    15: 'AUTH_USER',
    16: 'ANONYM_USER',
}


crypto_parameters = {
  'start': '1',
  'limit': '5000',
  'convert': 'USD'
}
crypto_headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': CMC_API_KEY,
}

CITIES = {'Минск': [53.842316, 27.695950],}



AI_MODEL = 'gpt-4o-mini'
AI_ROLE = 'user'
AI_SYSTEM_ROLE = {
                "role": "system",
                "content": "Отвечаешь преимущественно на русском языке."

            }
AI_MAX_TOKENS = 1000
AI_HEADERS = {
    'Authorization': f'Bearer {AI_API_KEY}'
}

