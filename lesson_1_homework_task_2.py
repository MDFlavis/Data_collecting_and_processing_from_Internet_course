'''Зарегистрироваться на https://openweathermap.org/api и написать функцию,
которая получает погоду в данный момент для города, название которого получается через input.
https://openweathermap.org/current'''

import os
import requests
import json
from dotenv import load_dotenv


def city_weather():
    """
           function to get the weather in the requested city
           :param:
           :return: str; status of weather
           """

    load_dotenv('./.env')

    city_name = str(input('Введите название города: '))
    key = 'API_KEY'
    api_key = os.getenv(key)

    # request longitude and latitude for our city
    geocoding_req = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}')
    data = json.loads(geocoding_req.text)
    lat = data[0]['lat']
    lon = data[0]['lon']

    # request weather for our city
    weather_req = requests.get(f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}')
    data = json.loads(weather_req.text)
    weather = data['weather'][0]['main']
    status = f'In {city_name} now is {weather}'
    return status


my_var = city_weather()

print(my_var)
