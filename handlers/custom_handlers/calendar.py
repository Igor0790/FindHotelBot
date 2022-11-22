from datetime import date

from telebot.types import CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from keyboards.inline import inline_boards
from keyboards.reply import reply_boards
from loader import bot
from states.bot_state import BotState
from utils.other_utils import get_calendar

ALL_LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(call: CallbackQuery):
    """
    Вывод календаря, сохранение дат в оперативной памяти.
    """
    today = date.today()
    result, key, step = get_calendar(calendar_id=1,
                                     current_date=today,
                                     min_date=today,
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:
        bot.edit_message_text(f"Выберите {ALL_LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f"Вы выбрали {result}, сохраняем")
        with bot.retrieve_data(call.message.chat.id) as data:
            data['date_in'] = result

        calendar, step = get_calendar(calendar_id=2,
                                      min_date=result,
                                      locale="ru",
                                      )
        bot.send_message(call.from_user.id,
                         f"Выберите {ALL_LSTEP[step]}",
                         reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal(call: CallbackQuery):
    """
    Вывод календаря, сохранение дат в оперативной памяти.
    """
    today = date.today()
    with bot.retrieve_data(call.message.chat.id) as data:
        date_in = data['date_in']
    result, key, step = get_calendar(calendar_id=2,
                                     current_date=today,
                                     min_date=date_in,
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:
        bot.edit_message_text(f"Выберите {ALL_LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f"Вы выбрали {result}, Сохраняем.")
        with bot.retrieve_data(call.message.chat.id) as data:
            data['date_out'] = result
            date_in = data['date_in']
        bot.send_message(call.message.chat.id, f'Вы выбрали даты приезда {date_in} и  отъезда {result}, правильно?', reply_markup=inline_boards.answer_board())

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(call: CallbackQuery):
    """
    Вывод календаря, сохранение дат в оперативной памяти.
    """
    today = date.today()
    result, key, step = get_calendar(calendar_id=1,
                                     current_date=today,
                                     min_date=today,
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:
        bot.edit_message_text(f"Выберите {ALL_LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f"Вы выбрали {result}, сохраняем")
        with bot.retrieve_data(call.message.chat.id) as data:
            data['date_in'] = result

        calendar, step = get_calendar(calendar_id=2,
                                      min_date=result,
                                      locale="ru",
                                      )
        bot.send_message(call.from_user.id,
                         f"Выберите {ALL_LSTEP[step]}",
                         reply_markup=calendar)


@bot.callback_query_handler(func=lambda call: call.data == 'Yes')
def yes_doing(call: CallbackQuery):
    """
    Callback, переключающий состояние на следующий этап поиска отелей.
    """
    with bot.retrieve_data(call.message.chat.id) as data:
        command = data.get('SORT')
    if command == '/lowprice' or command == '/highprice':
        bot.set_state(call.from_user.id, BotState.photo, call.message.chat.id)
    else:
        bot.set_state(call.from_user.id, BotState.photo_for_bestdeal, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Отлично, продолжаем! Нажмите кнопку ниже', reply_markup=reply_boards.next())






@bot.callback_query_handler(func=lambda call: call.data == 'No')
def no_doing(call: CallbackQuery):
    """
    Callback, переключающий состояние на начальный этап поиска отелей.
    """
    bot.set_state(call.from_user.id, BotState.hotel, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Попробуйте еще раз. Для этого нужно вызвать функцию поиска отелей заново', reply_markup=reply_boards.in_state_photo())
