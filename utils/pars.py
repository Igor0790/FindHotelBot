import json
import os
import re
from datetime import datetime
from json import JSONDecodeError

import requests
from telebot.types import Message

from config_data.config import RAPID_API_KEY
from loader import database, option, bot


def data_pars_city(city: str, message: Message) -> (list, None):
    """
    Функция поиска населенного пункта пользователя
    :param city: город, введенный пользователем
    :return: int - если результат обращения к API не пустой, в ином случае None
    """
    querystring = {"query": city, "locale":"ru_RU"}
    my_req = requests.request('GET', url='https://hotels4.p.rapidapi.com/locations/v2/search', headers=option, params=querystring)
    data = json.loads(my_req.text)
    city_list = []
    try:
        for value in data['suggestions'][0]['entities']:
            city_list.append((value['name'], value['destinationId']))
        return city_list
    except TypeError as e:
        bot.send_message(message.chat.id, 'Ничего не найдено.')
        return None


def data_pars_hotels(UID, city:str, querystring: dict) -> (int, None):
    """
    Получает номер destid города, и заполняет БД данными о отелях в этом городе.
    :param destid: номер города
    :param UID: уникальный номер пользователя телеграмм, для создания многопользовательского режима

    """
    create_new_table = f"""
            CREATE TABLE IF NOT EXISTS hotels_{city}_{UID} (
              id SERIAL PRIMARY KEY,
              destid BIGINT,
              name TEXT NOT NULL, 
              address TEXT NOT NULL,
              landmarks TEXT NOT NULL,
              price TEXT
            )
            """

    database.execute_query(create_new_table)

    response = requests.request("GET", url='https://hotels4.p.rapidapi.com/properties/list', headers=option, params=querystring)

    try:
        data = json.loads(response.text)
    except JSONDecodeError:
        print('Проблемный запрос: ', response)
        return None


    hotels_list = []

    for value in data['data']['body']['searchResults']['results']:
        hotels_list.append((value.get('id', 'None'), value.get('name', 'None'),
                            value.get('address', 'None').get('countryName', 'None') + ', ' +
                            value.get('address', 'None').get('locality', 'None') + ' ' + value.get('address', 'None').get('streetAddress', 'None'),
                            re.sub(r',', '.', value.get('ratePlan', 'None').get('price', 'None').get('current', 'None')[1:]),
                            value.get('landmarks', None)[0].get('distance', None)))

    if hotels_list:
        hotel_records = ", ".join(["%s"] * len(hotels_list))
        insert_query_str = (
            f"INSERT INTO hotels_{city}_{UID} (destid, name, address, price, landmarks ) VALUES {hotel_records}")
        database.insert_query(insert_query_str, hotels_list)
    else:
        return None
    return 1

def pars_hotel_photo(destid: int, UID, city: str) -> None:
    """
    Функция получает номер отеля, обращается к API сайта.
    :param destid: номер отеля (destid)
    :param UID: уникальный номер пользователя телеграмм, для создания многопользовательского режима
    :return: список URL фото отеля
    """
    create_new_table = f"""
            CREATE TABLE IF NOT EXISTS photo_{city}_{UID}_{destid} (
              id SERIAL PRIMARY KEY,
              URL TEXT NOT NULL
            )
            """
    database.execute_query(create_new_table)


    querystring = {"id": destid}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response = requests.request("GET", url="https://hotels4.p.rapidapi.com/properties/get-hotel-photos", headers=headers, params=querystring)
    data = json.loads(response.text)

    photo_list = []
    for hotels in data['hotelImages']:
        for key, value in hotels.items():
            if key == 'baseUrl':
                temp = (re.sub(r'{size}', 'z', value),)
                photo_list.append(temp)

    hotel_records = ", ".join(["%s"] * len(photo_list))
    insert_query_str = (f"INSERT INTO photo_{city}_{UID}_{destid} (url) VALUES {hotel_records}")

    database.insert_query(insert_query_str, photo_list)

def change_type_value_number(number) -> (int, None):
    """
    Функция для обработки данных из БД, так как они могут быть в разном формате, а вернуть нужно только int
    """
    if isinstance(number, int):
        return number
    elif isinstance(number, float):
        num_len = len(str(number))
        while number > 1:
            number /= 10
        return int(str(number)[2:num_len+1]) + 1
    elif isinstance(number, str):
        if ',' in number:
            re.sub(',', '.', number)
            return change_type_value_number(number)
        elif '.' in number:
            number = float(number)
            return change_type_value_number(number)
        else:
            return int(number)
    else:
        return None










