from config import (
                    URL_SERVER_API,
                    headers,)

from modules.ovay_api_gower import ApiClient


api_ov_client = ApiClient(URL_SERVER_API, headers)
