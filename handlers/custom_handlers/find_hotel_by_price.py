import os
from datetime import datetime, date
import json

from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import LSTEP

from keyboards.inline import inline_boards
from loader import bot, database
from states.bot_state import BotState
from utils.other_utils import get_calendar
from utils.pars import data_pars_hotels, data_pars_city, pars_hotel_photo, change_type_value_number


@bot.message_handler(commands=['lowprice', 'highprice'])
def get_lowprice(message: Message) -> None:

    database.delete_all()
    bot.set_state(message.from_user.id, BotState.hotel, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}. в каком городе ищем? Требуется ввести город на русском языке за пределами РФ.')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['SORT'] = message.text



@bot.message_handler(state=BotState.hotel)
def find_city(message: Message) -> None:
    """
    Состояние выбора города, запуск календаря
    """

    city_list = message.text.lower().split()
    if len(city_list) == 1:
        city = city_list[0]
    else:
        city = '_'.join(city_list)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = city

    today = date.today()
    calendar, step = get_calendar(calendar_id=1, current_date=today, min_date=today, locale="ru")
    bot.send_message(message.chat.id, f"Выберите дату заезда: {LSTEP[step]}", reply_markup=calendar)

@bot.message_handler(state=BotState.photo)
def find_photo(message: Message) -> None:
    """
    Состояние выбора района города. Временные данные пользователя записываем в таблицу БД, чтобы потом вытащить их
    в callback
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        city = data['city']
        date_in = data['date_in']
        date_out = data['date_out']
        command = data['SORT']

    database.set_temp_data(message.chat.id, city, date_in, date_out, command)

    city_list = data_pars_city(city, message)
    bot.set_state(message.from_user.id, BotState.no_state, message.chat.id)
    if city_list:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите интересующий вас район', reply_markup=inline_boards.find_city_area(city_list), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Такой город не найден. Попробуйте еще раз.')

@bot.callback_query_handler(func=lambda call: call.data.startswith('{"city') == True)
def callback_query(call: CallbackQuery):
    """
    Обработчик, запускающий функции парсинга. Заполняется БД, выдается inline клавиатура, в которой через call.data передаюдтся счетчики строк в БД.
    Пагинация работает через callback.

    photo_row - номер строки в таблице с фото
    hostel_row - номер строки в таблице с отелями
    :return: None
    """
    json_string = json.loads(call.data)
    destid_city = int(json_string['city'])

    data_list = database.get_lines(f'select * from temp_data where user_id = \'{call.message.chat.id}\'')[0]
    city = data_list[2]
    date_in = data_list[3]
    date_out = data_list[4]
    nums_days = int(data_list[5])
    command = data_list[6]

    photo_row = 0
    hostel_row = 0
    hostel_data = None
    photo_list = None
    price_hotel = None
    hotel_id = 0
    try:
        if command == '/lowprice':
            querystring = {"destinationId": destid_city, "pageNumber": "1", "pageSize": "25", "checkIn": date_in,
                            "checkOut": date_out, "adults1": "1", "locale": "en_US", "sortOrder": 'PRICE_LOWEST_FIRST'}

            bot.send_message(call.message.chat.id, 'Ищем, сортируем отели по цене, начиная с недорогих...')
            data_pars_hotels(UID=call.message.chat.id, city=city, querystring=querystring)
        elif command == '/highprice':

            querystring = {"destinationId": destid_city, "pageNumber": "1", "pageSize": "25", "checkIn": date_in,
                           "checkOut": date_out, "adults1": "1", "locale": "en_US", "sortOrder": 'PRICE_HIGHEST_FIRST'}
            bot.send_message(call.message.chat.id, 'Ищем, сортируем отели по цене, начиная с более дорогих...')
            data_pars_hotels(UID=call.message.chat.id, city=city, querystring=querystring)

        hostel_data = database.get_lines(f'select * from hotels_{city}_{call.message.chat.id} '
                                             f'OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY')
        hotel_id = hostel_data[0][1]

        pars_hotel_photo(hotel_id, call.message.chat.id, city)
        photo_list = database.get_lines(f'select url from photo_{city}_{call.message.chat.id}_{hostel_data[0][1]} '
                                            f'OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY')

        price_hotel = change_type_value_number(hostel_data[0][5]) * nums_days
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Что-то пошло не так во время поиска. Попробуйте перезапустить бота. '
                                          'Если это не помогло - сообщите разработчику. Спасибо.')
        with open(os.path.join('..', '..', 'logs_bot.txt'), 'a+', encoding='utf-8') as file:
            file.write(f'user: {call.message.chat.id}, ' + str(datetime.now()) + '\n')
            file.write(str(e) + '\n')
            file.write(str(city) + str(command) + '\n')
            file.write('------------------------------\n')
        bot.delete_state(call.message.from_user.id, call.message.chat.id)



    text = f'<b>Название отеля:</b> {hostel_data[0][2]}\n' \
           f'<b>Адрес отеля: </b>{hostel_data[0][3]}\n' \
           f'<b>Цена за сутки:</b> {price_hotel}$\n' \
           f'<b>Цена за выбранные {nums_days} суток: </b>{price_hotel}$\n' \
           f'<b>Расстояние до центра города: </b> {hostel_data[0][4]}\n' \
           f'<b>Забронировать:</b> https://www.hotels.com/ho{hotel_id}'

    bot.send_photo(call.message.chat.id, photo_list[0][0], caption=text, parse_mode='HTML',
               reply_markup=inline_boards.pagination(photo_row, city, nums_days, hostel_row))

    data_for_logs = [(hostel_data[0][2], hostel_data[0][3], price_hotel, price_hotel * nums_days,
                           hostel_data[0][4], photo_list[0][0], str(date.today()), command, hotel_id)]
    database.add_log(uid=call.message.chat.id, data=data_for_logs)




