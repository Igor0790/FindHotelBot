from telegram_bot_calendar import DetailedTelegramCalendar

def get_calendar(is_process=False, callback_data=None, **kwargs):
    if is_process:
        result, key, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                     current_date=kwargs.get('current_date'),
                                                     min_date=kwargs['min_date'],

                                                     locale=kwargs['locale']).process(callback_data.data)
        return result, key, step
    else:
        calendar, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                  current_date=kwargs.get('current_date'),
                                                  min_date=kwargs['min_date'],
                                                  locale=kwargs['locale']).build()
        return calendar, step

def return_list(data: str) -> (list, None):

    if '-' in data:
        return data.split('-')
    elif ' ' in data:
        return data.split()
    elif ',' in data:
        return data.split(',')
    else:
        return int(data)
    #return None