from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def answer_board() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Нет!', callback_data='No')
    button2 = InlineKeyboardButton(text='Да!', callback_data='Yes')
    markup.add(button1, button2)
    return markup

def pagination(photo_row: int, city: str, nums_days: int, hostel_row: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=f'Следующий отель!',
                                    callback_data="{\"hot\":\"1\","
                                                  "\"P\":\"" + str(photo_row) + "\","
                                                  "\"C\":\"" + str(city) + "\","
                                                  "\"D\":\"" + str(nums_days) + "\","
                                                  "\"H\":\"" + str(hostel_row + 1) + "\"}"),
               InlineKeyboardButton(text=f'Еще фото! ->',
                                    callback_data="{\"met\":\"1\","
                                                  "\"P\":\"" + str(photo_row + 1) + "\","
                                                  "\"D\":\"" + str(nums_days) + "\", "
                                                  "\"C\":\"" + str(city) + "\",\"H\":\"" + str(hostel_row) + "\"}"))
    return markup

def paginnation_for_history(user_data_row: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Следующий!', callback_data='{\"user\":\"1\",'
                                                                            '\"row\":\"' + str(user_data_row) + '\"}'))


    return markup

def find_city_area(data_list: list[tuple]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for area in data_list:
        markup.add(InlineKeyboardButton(text=area[0], callback_data='{\"city\":\"' + str(area[1]) + '\"}'
                                        ))
    return markup

def find_city_area_best(data_list: list[tuple]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for area in data_list:
        markup.add(InlineKeyboardButton(text=area[0], callback_data='{\"ci_b\":\"' + str(area[1]) + '\"}'
                                        ))
    return markup