import os
import telebot
import dotenv

import google_sheet

#Load API KEY from secure .env file 
dotenv.load_dotenv()

# Constants
API_KEY: str  = os.getenv("API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDS_PATH = os.getenv("CREDS_PATH")

ADD_TOPIC_BUTTON_NAME: str = "Add new topic"
ADD_TOPIC_SUCCESS_ANSWER: str = "Напишите название темы для добавления"
ADD_TOPIC_SUCCESS_ADDED: str = "Добавлена"
ADD_TOPIC_SUCCESS_DELAYED: str = "Отложено на 1 день"
ADD_TOPIC_SUCCESS_STAGED: str = "Успешно повторили"
SHOW_ACTIVE_TOPICS_BUTTON_NAME: str  = "Show active topics"
START_MESSAGE: str  = "Choose an action"

#init bot
bot = telebot.TeleBot(API_KEY)
api = google_sheet.GoogleSheetAPI(SPREADSHEET_ID, CREDS_PATH)

@bot.message_handler(commands=["show"])
def get_topics(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    active_topics = api.get_all_active_topics()
    for topic in active_topics:
        bot.send_message(message.chat.id, topic)

@bot.message_handler(commands=["add"])
def add_topic(message):
    api.append_topic(message.text.replace('/add', ''), 'nikitaff')
    bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_ADDED)

@bot.message_handler(commands=["delay"])
def add_topic(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    active_topics = api.get_all_active_topics()
    for topic in active_topics:
        topic_button = telebot.types.KeyboardButton(topic)
        markup.add(topic_button)
    bot.send_message(message.chat.id, 'Выберите топик', reply_markup=markup)
    api.delay_topic(message)
    bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_DELAYED)

@bot.message_handler(commands=["stage"])
def add_topic(message):
    api.stage_topic(message.text.replace('/stage ', ''))
    bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_STAGED)

bot.polling(non_stop=True, interval=0)


