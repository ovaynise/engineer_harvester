from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests

from inits.logger import other_logger


class Crypto:
    def __init__(self, url, headers, params):
        self.url = url
        self.headers = headers
        self.params = params

    def show_btc(self):
        try:
            response = requests.get(self.url,
                                    headers=self.headers,
                                    params=self.params)
            other_logger.debug(
                f'Успешно получили ответ '
                f'Крипто сервера: {response.status_code}'
            )
            price = response.json().get('data')[0].get('quote').get('USD').get('price')
            symbol = response.json().get('data')[0].get('name')
            other_logger.debug(f'Успешно сформировали сообщение для отправки')
            return f'{symbol} : {round(price,2)} $'

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            other_logger.error(f'Ошибка - {e}')
