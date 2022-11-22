from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def answer_board() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton('Нет!')
    button2 = KeyboardButton('Да!')
    markup.add(button1, button2)
    return markup

def in_start() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('В начало')
    markup.add(button1)
    return markup

def in_state_photo() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Заново выбрать дату!')
    markup.add(button1)
    return markup

def next() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton('Вперед!')
    markup.add(button1)
    return markup