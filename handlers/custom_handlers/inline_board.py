import json
from datetime import date

from telebot.types import CallbackQuery, InputMediaPhoto

from keyboards.inline import inline_boards
from loader import bot, database
from utils.pars import pars_hotel_photo, change_type_value_number


@bot.callback_query_handler(func=lambda call: call.data.startswith('{"met') == True)
def callback_query(call: CallbackQuery):
    """
    Обработчик, отвечающий за перелистывание фото. Переменные получены из call.data
    :return: None
    photo_row - номер строки в таблице с фото
    hostel_row - номер строки в таблице с отелями
    """
    json_string = json.loads(call.data)
    photo_row = int(json_string['P'])
    hostel_row = int(json_string['H'])
    city = json_string['C']
    nums_days = int(json_string['D'])


    hostel_data = database.get_lines(f'select * from hotels_{city}_{call.message.chat.id} '
                                     f'OFFSET {hostel_row} ROWS FETCH NEXT 1 ROWS ONLY')

    photo_list = database.get_lines(f'select url from photo_{city}_{call.message.chat.id}_{hostel_data[0][1]} '
                                    f'OFFSET {photo_row} ROWS FETCH NEXT 1 ROWS ONLY')
    if photo_list:
        price_hotel = change_type_value_number(hostel_data[0][5])

        text = f'<b>Название отеля:</b> {hostel_data[0][2]}\n' \
               f'<b>Адрес отеля: </b>{hostel_data[0][3]}\n' \
               f'<b>Цена за сутки: {price_hotel}$</b>\n' \
               f'<b>Цена за выбранные {nums_days} суток: </b>{price_hotel * nums_days}$\n' \
               f'<b>Расстояние до центра города: </b> {hostel_data[0][4]}\n' \
               f'<b>Забронировать:</b> https://www.hotels.com/ho{hostel_data[0][1]}'

        bot.edit_message_media(media=InputMediaPhoto(media=photo_list[0][0], caption=text, parse_mode='HTML'), message_id=call.message.message_id,
                               chat_id=call.message.chat.id, reply_markup=inline_boards.pagination(photo_row, city, nums_days, hostel_row))

    else:
        bot.send_message(call.message.chat.id, 'Фото закончились. Пожалуйста, выберите следующий отель для просмотра.')

@bot.callback_query_handler(func=lambda call: call.data.startswith('{"hot') == True)
def callback_query(call: CallbackQuery):
    """
    Обработчик, отвечающий за перелистывание отелей.
    Получает номер города из БД, вызывает функцию заполнения БД фото этого отеля

    :return: None
    """

    json_string = json.loads(call.data)
    photo_row = 0
    hostel_row = int(json_string['H'])
    city = json_string['C']
    nums_days = int(json_string['D'])

    hostel_data = database.get_lines(f'select * from hotels_{city}_{call.message.chat.id} '
                                     f'OFFSET {hostel_row} ROWS FETCH NEXT 1 ROWS ONLY')

    pars_hotel_photo(hostel_data[0][1], call.message.chat.id, city)
    photo_list = database.get_lines(f'select url from photo_{city}_{call.message.chat.id}_{hostel_data[0][1]} '
                                    f'OFFSET {photo_row} ROWS FETCH NEXT 1 ROWS ONLY')
    if hostel_data:

        price_hotel = change_type_value_number(hostel_data[0][5])

        text = f'<b>Название отеля:</b> {hostel_data[0][2]}\n' \
               f'<b>Адрес отеля: </b>{hostel_data[0][3]}\n' \
               f'<b>Цена за сутки: {price_hotel}$</b>\n' \
               f'<b>Цена за выбранные {nums_days} суток: </b>{price_hotel * nums_days}$\n' \
               f'<b>Расстояние до центра города: </b> {hostel_data[0][4]}\n' \
               f'<b>Забронировать:</b> https://www.hotels.com/ho{hostel_data[0][1]}'

        bot.edit_message_media(media=InputMediaPhoto(media=photo_list[0][0], caption=text, parse_mode='HTML'),
                               message_id=call.message.message_id, chat_id=call.message.chat.id,
                               reply_markup=inline_boards.pagination(photo_row, city, nums_days, hostel_row))

        data_for_logs = [(hostel_data[0][2], hostel_data[0][3], price_hotel, price_hotel * nums_days,
                                  hostel_data[0][4], photo_list[0][0], str(date.today()), '0', hostel_data[0][1])]
        database.add_log(uid=call.message.chat.id, data=data_for_logs)
    else:
        bot.send_message(call.message.chat.id, 'Отели закончились. Пожалуйста, выберите что-то другое.')