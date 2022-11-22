from telebot.types import Message, CallbackQuery, InputMediaPhoto
import json

from keyboards.inline import inline_boards
from loader import bot, database
from states.bot_state import BotState


@bot.message_handler(commands=['history'])
def get_history(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Вы запустили просмотр ваших действий. Смотрим!')
    user_data_row = 0
    print('попал в функцию истории!', user_data_row)

    try:
        user_data = database.get_lines(f'select * from history_{message.chat.id} '
                                       f'OFFSET {user_data_row} ROWS FETCH NEXT 1 ROWS ONLY')[0]
    except TypeError as e:
        user_data = None

    if user_data:
        text = f'<b>Запущенная команда:</b> {user_data[8]}\n' \
               f'<b>Дата запуска: </b>{user_data[7]}\n' \
               f'<b>Название отеля: </b>{user_data[1]}\n' \
               f'<b>Адрес отеля: </b>{user_data[2]}\n' \
               f'<b>Цена за сутки при поиске: </b>{user_data[3]}$\n' \
               f'<b>Расстояние до центра: </b>{user_data[5]}\n' \
               f'<b>Забронировать: https://www.hotels.com/ho{user_data[9]}</b>'
        bot.send_photo(chat_id=message.chat.id, photo=user_data[6], caption=text, parse_mode='HTML',
                       reply_markup=inline_boards.paginnation_for_history(user_data_row + 1))
    else:
        bot.send_message(message.chat.id, 'История поиска в данный момент пустая, вы еще ничего не смотрели!')


@bot.callback_query_handler(func=lambda call: call.data.startswith('{"user') == True)
def callback_query(call: CallbackQuery):
    """
    Обработчик пагинации клавиатуры. Через call,data передаются и получаются переменная - номер строки в БД.
    while нужен, чтобы корректно показать запущенную команду (т.к. она будет 0, если отели листали не меняя запущенную команду)
    temp_row_counter: временная переменная, нужная для смены строки БД без влияния на основную переменную
    """
    json_string = json.loads(call.data)
    user_data_row = int(json_string['row'])
    print('попал в коллбек истории!', user_data_row)
    command = None

    try:
        user_data = database.get_lines(f'select * from history_{call.message.chat.id} '
                                       f'OFFSET {user_data_row} ROWS FETCH NEXT 1 ROWS ONLY')[0]
        command = user_data[8]
        temp_row_counter = user_data_row
        while command == '0':
            temp_row_counter -= 1
            command = database.get_lines(f'select command from history_{call.message.chat.id} '
                                         f'OFFSET {temp_row_counter} ROWS FETCH NEXT 1 ROWS ONLY')[0][0]
            print(user_data_row, temp_row_counter, command)

    except Exception as e:
        user_data = None

    if user_data:

        text = f'<b>Запущенная команда:</b> {command}\n' \
               f'<b>Дата запуска: </b>{user_data[7]}\n' \
               f'<b>Название отеля: </b>{user_data[1]}\n' \
               f'<b>Адрес отеля: </b>{user_data[2]}\n' \
               f'<b>Цена за сутки при поиске: </b>{user_data[3]}$\n' \
               f'<b>Расстояние до центра: </b>{user_data[5]}\n' \
               f'<b>Забронировать: </b> https://www.hotels.com/ho{user_data[9]}'

        bot.edit_message_media(media=InputMediaPhoto(media=user_data[6], caption=text, parse_mode='HTML'),
                               message_id=call.message.message_id, chat_id=call.message.chat.id,
                               reply_markup=inline_boards.paginnation_for_history(user_data_row + 1))
    else:
        bot.send_message(call.message.chat.id, 'История просмотров закончилась. Пожалуйста, выберите другую команду.')
