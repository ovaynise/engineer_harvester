import requests

from inits.logger import other_logger
from config import API_WEATHER_KEY, CITIES


class WeatherShow:
    def __init__(self, city):
        if city not in CITIES:
            other_logger.error(f"Город {city} не найден в списке.")
            raise ValueError(f"Город {city} не найден в списке.")
        self.city = city
        self.lat, self.lon = CITIES[city]

    @staticmethod
    def kelvin_to_celsius(kelvin):
        return kelvin - 273.15

    def get_api_answer(self):
        URL = f'https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={API_WEATHER_KEY}&lang=ru'
        response = requests.get(URL)
        other_logger.debug(
            f'Успешно получен ответ от сервера погода: {response.status_code}'
        )
        return response.json()

    def get_name(self):
        response = self.get_api_answer()
        other_logger.debug(
            f'Успешно получен запрос имени: {response.status_code}')
        return response.get('name')

    def info(self):
        response = self.get_api_answer()
        temp = round(self.kelvin_to_celsius(response.get('main').get('temp')), 2)
        temp_feels_like = round(
            self.kelvin_to_celsius(response.get('main').get('feels_like')), 2)
        name_city = response.get('name')
        wind_speed = response.get('wind').get('speed')
        weather_description = response.get('weather')[0].get('description')
        message = (
            f'Погода в г.{self.city} ({name_city}):\n Температура = {temp:.2f} C ,{weather_description} '
            f'\n Ощущается как {temp_feels_like} С'
            f'\n Скорость ветра {wind_speed} м/с')
        other_logger.debug(
            f'Функция вернула сформированное сообщение message ')
        return message
