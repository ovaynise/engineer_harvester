import aiohttp
from dotenv import load_dotenv

from inits.logger import db_logger

load_dotenv()


class ApiClient:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    async def get(self, endpoint):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}{endpoint}',
                                   headers=self.headers) as response:
                if response.status != 200:
                    db_logger.error(
                        f'Error:Ошибка GET запроса к endpoint: '
                        f'адрес: {self.url}{endpoint}:Вернулся статус код: '
                        f'{response.status}')
                    return None
                db_logger.debug(f'Успешно отправлен GET[{response.status}] '
                                f'запрос в БД к '
                                f'эндпоину адрес: {self.url}{endpoint}')

                return await response.json()

    async def post(self, endpoint, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.url}{endpoint}', json=data,
                                    headers=self.headers) as response:
                if response.status != 201:
                    db_logger.error(
                        f'Error:Ошибка POST'
                        f' запроса к endpoint адрес: {self.url}{endpoint}'
                        f':Вернулся статус код: '
                        f'{response.status}')
                    return None
                db_logger.debug(f'Успешно '
                                f'отправлен POST[{response.status}] '
                                f'запрос в БД к '
                                f'эндпоину адрес: {self.url}{endpoint}')
                return await response.json()

    async def patch(self, endpoint, data, pk):
        async with aiohttp.ClientSession() as session:
            async with session.patch(f'{self.url}{endpoint}{pk}/',
                                     json=data,
                                     headers=self.headers) as response:
                if response.status != 200:
                    db_logger.error(
                        f'Error:Ошибка PATCH запроса к endpoint'
                        f' адрес: {self.url}{endpoint}:Вернулся статус код: '
                        f'{response.status}')
                    return None
                db_logger.debug(f'Успешно отправлен PATCH[{response.status}] '
                                f'запрос в БД к '
                                f'эндпоину адрес: {self.url}{endpoint}')
                return await response.json()

    async def put(self, endpoint, data, pk):
        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self.url}{endpoint}{pk}/', json=data,
                                   headers=self.headers) as response:
                if response.status != 200:
                    db_logger.error(
                        f'Error:Ошибка PUT запроса к endpoint'
                        f' {self.url}{endpoint}:Вернулся статус код: '
                        f'{response.status}')
                    return None
                db_logger.debug(f'Успешно отправлен PUT[{response.status}] '
                                f'запрос в БД к '
                                f'эндпоину адрес: {self.url}{endpoint}')
                return await response.json()

    async def delete(self, endpoint, pk):
        async with aiohttp.ClientSession() as session:
            async with session.delete(f'{self.url}{endpoint}{pk}/',
                                      headers=self.headers) as response:
                if response.status != 204:
                    db_logger.error(
                        f'Error:Ошибка DELETE запроса к endpoint'
                        f' {self.url}{endpoint}:Вернулся статус код: '
                        f'{response.status}')
                    return None
                db_logger.debug(f'Успешно отправлен DELETE[{response.status}] '
                                f'запрос в БД к '
                                f'эндпоину адрес: {self.url}{endpoint}')
                return {'status': 'deleted'}

    async def get_status_code(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{url}',
                                   headers=self.headers) as response:
                print(f'{response.status} - {url}')
                if response.status != 200:
                    db_logger.error(
                        f'Error:Ошибка GET запроса к endpoint: '
                        f'адрес: {url}:Вернулся статус код: '
                        f'{response.status}')
                    return None
                db_logger.debug(f'Успешно отправлен GET[{response.status}] '
                                f'запрос в БД к эндпоину адрес: {url}')

                return await response.json()
