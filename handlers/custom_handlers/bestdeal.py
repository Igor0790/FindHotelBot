import json
from datetime import date

from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from telegram_bot_calendar import LSTEP

from keyboards.inline import inline_boards
from keyboards.reply import reply_boards
from loader import bot, database
from states.bot_state import BotState
from utils.other_utils import return_list, get_calendar
from utils.pars import data_pars_hotels, data_pars_city, pars_hotel_photo, change_type_value_number


@bot.message_handler(commands=['bestdeal'])
def get_lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, BotState.answer, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}. Вы запустили поиск отелей по вашим условиям. В каком городе'
                                           f' искать? Требуется ввести город на русском языке за пределами РФ.')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['SORT'] = message.text



@bot.message_handler(state=BotState.answer)
def price_answer(message: Message) -> None:
    bot.send_message(message.chat.id, 'Секунду, проверяю наличие города...')
    city_list = message.text.lower().split()

    if len(city_list) == 1:
        city = city_list[0]
    else:
        city = '_'.join(city_list)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = city

    city_list = data_pars_city(city, message)
    bot.set_state(message.from_user.id, BotState.price, message.chat.id)
    if city_list:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите интересующий вас район',
                         reply_markup=inline_boards.find_city_area_best(city_list), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено. Попробуйте еще раз.')

@bot.callback_query_handler(func=lambda call: call.data.startswith('{"ci_b') == True)
def callback_query_inline(call: CallbackQuery):

    json_string = json.loads(call.data)
    destid_city = int(json_string['ci_b'])

    create_new_table = f"""
            CREATE TABLE IF NOT EXISTS temp_data (
              id SERIAL PRIMARY KEY,
              user_id TEXT,
              city TEXT,
              DATE_IN TEXT,
              DATE_OUT TEXT,
              num_days TEXT,
              COMMAND TEXT
            )
            """
    database.execute_query(create_new_table)
    database.execute_query(f'insert into temp_data (user_id, city) values ({call.message.chat.id}, {destid_city})')


    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton(text='0-600'),
                KeyboardButton(text='601-900'),
                KeyboardButton(text='901-1200'),
                KeyboardButton(text='1201-1500'))

    bot.send_message(call.message.chat.id, 'Принято. На кнопках ниже выберите нужный вам дипазон цен за сутки, либо введите свой диапазон.', reply_markup=markup)



@bot.message_handler(state=BotState.price)
def landmark_answer(message: Message) -> None:
    price = return_list(message.text)

    if price:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton(text='3'),
                   KeyboardButton(text='6'),
                   KeyboardButton(text='8'),
                   KeyboardButton(text='10'))
        bot.set_state(message.from_user.id, BotState.landmark, message.chat.id)
        bot.send_message(message.chat.id,
                         'Принято. Теперь подскажите, как далеко отель должен находиться от отеля? Вводить в милях.', reply_markup=markup)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_min'] = price[0]
            data['price_max'] = price[1]
    else:
        bot.send_message(message.chat.id,
                         'Введено какое-то непонятное для меня значение. Пожалуйста, попробуйте еще раз.'
                         'Например, можно ввести диапазон цен в таком же виде как на кнопках ранее. Требуется перезапустить поиск.')
        bot.delete_state(message.from_user.id, message.chat.id)




@bot.message_handler(state=BotState.landmark)
def photo_answer(message: Message) -> None:
    landmark = return_list(message.text)
    if landmark:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['landmark_min'] = landmark
        today = date.today()
        calendar, step = get_calendar(calendar_id=1, current_date=today, min_date=today, locale="ru")
        bot.send_message(message.chat.id, f"Теперь выберите дату заезда: {LSTEP[step]}", reply_markup=calendar)
    else:
        bot.send_message(message.chat.id, 'Введено какое-то непонятное для меня значение. Пожалуйста, попробуйте еще раз.'
                                          'Например, можно ввести растояние в таком же виде как на кнопках ранее. Требуется перезапустить поиск.')
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=BotState.photo_for_bestdeal)
def find_photo(message: Message) -> None:
    """
    Функция, запускающая сам парсинг. Заполняется БД, выдается inline клавиатура, в которой через call.data передаюдтся счетчики строк в БД.
    Пагинация работает через callback.

    photo_row: номер строки в таблице с фото
    hostel_row: номер строки в таблице с отелями
    landmark: Расстояние до центра
    price_min: минимальная цена отеля
    price_max: максимальная цена отеля
    city: город, где ведется поиск
    city_num: DESTID отеля, получается из API
    date_in: дата приезда
    date_out: дата отъезда
    nums_days: количество суток, планируемых для отдыха в отеле
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        landmark = data['landmark_min']
        price_min = data['price_min']
        price_max = data['price_max']
        city = data['city']
        date_in = data['date_in']
        date_out = data['date_out']
        command = data['SORT']

    city_num = database.get_lines(f'select city from temp_data order by city limit 1')[0][0]
    nums_days = (date_out - date_in).days

    bot.send_message(message.chat.id, 'Запускаю поиск отелей....')
    photo_row = 0
    hostel_row = 0

    queue = {"destinationId":str(city_num),"pageNumber":"1","pageSize":"25","checkIn":str(date_in),
                          "checkOut":str(date_out),"adults1":"1","sortOrder":"PRICE","priceMin": str(price_min),
                    "priceMax": str(price_max), "locale":"en_US","currency":"USD", "landmarkIds": '0' + '-' + str(landmark)}

    result_request = data_pars_hotels(UID=message.chat.id, city=city, querystring=queue)
    if result_request == None:
        bot.send_message(message.chat.id, 'функция вернула None.')
        print('RESULT: ', result_request)


    hostel_data = database.get_lines(f'select * from hotels_{city}_{message.chat.id} OFFSET 0 \
                                        ROWS FETCH NEXT 1 ROWS ONLY')
    if hostel_data:
        pars_hotel_photo(hostel_data[0][1], message.chat.id, city)
        photo_list = database.get_lines(f'select url from photo_{city}_{message.chat.id}_{hostel_data[0][1]} '
                                            f'OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY')

        price_hotel = change_type_value_number(hostel_data[0][5])

        text = f'<b>Название отеля:</b> {hostel_data[0][2]}\n' \
                f'<b>Адрес отеля: </b>{hostel_data[0][3]}\n' \
                f'<b>Цена за сутки:</b> {price_hotel}$\n' \
                f'<b>Цена за выбранные {nums_days} суток: </b>{price_hotel * nums_days}$\n' \
                f'<b>Расстояние до центра города: </b> {hostel_data[0][4]}\n' \
                f'<b>Забронировать:</b> https://www.hotels.com/ho{hostel_data[0][5]}'


        bot.send_photo(message.chat.id, photo_list[0][0], caption=text, parse_mode='HTML',
                           reply_markup=inline_boards.pagination(photo_row, city, nums_days, hostel_row))

        data_for_logs = [(hostel_data[0][2], hostel_data[0][3], price_hotel, price_hotel * nums_days,
                                  hostel_data[0][4], photo_list[0][0], str(date.today()), command, hostel_data[0][1])]
        database.add_log(uid=message.chat.id, data=data_for_logs)


        bot.set_state(message.from_user.id, BotState.no_state, message.chat.id)
    else:
        bot.set_state(message.from_user.id, BotState.answer, message.chat.id)
        bot.send_message(message.chat.id, 'К сожалению, по вашим запросам отелей не найдено. Пожалуйста, '
                                          'повторите поиск, выбрав новые условия. Начнем сначала, введите город для поиска.')





