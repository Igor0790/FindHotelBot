from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from database.data_hotel import Database


storage = StateMemoryStorage()

bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
option = {"X-RapidAPI-Key": config.RAPID_API_KEY, "X-RapidAPI-Host":"hotels4.p.rapidapi.com"}
database = Database(db_name=config.DB_NAME, db_user=config.DB_USER, db_password=config.DB_PASSWORD, db_host="127.0.0.1", db_port="5432")

