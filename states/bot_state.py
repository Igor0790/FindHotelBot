from telebot.handler_backends import State, StatesGroup

class BotState(StatesGroup):
    city = State()
    hotel = State()
    photo = State()
    photo_for_bestdeal = State()
    answer = State()
    price = State()
    landmark = State()
    no_state = State()
