from telebot.types import Message

from loader import bot
from states.bot_state import BotState


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!"
                          f"Буду рад вам помочь в поисках подходящего отеля в нужном вам городе. Перечень доступных команд вы найдете с помощью "
                          f"команды /help, или после перехода в меню. Для перехода из одного пункта меню в другой, сначала используйте команду /start.")
    bot.set_state(message.from_user.id, BotState.no_state, message.chat.id)

