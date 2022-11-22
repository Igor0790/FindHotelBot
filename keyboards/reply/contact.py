from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from loader import bot

def request_contact() -> ReplyKeyboardMarkup:
    keybord = ReplyKeyboardMarkup(True, True)
    keybord.add(KeyboardButton('Отправить контакт', request_contact=True))
    return keybord
