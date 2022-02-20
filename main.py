import os
import telebot
import dotenv

import google_sheet

#Load API KEY from secure .env file 
dotenv.load_dotenv()

# Constants
API_KEY: str  = os.getenv("API_KEY")
ADD_TOPIC_BUTTON_NAME: str = "Add new topic"
ADD_TOPIC_SUCCESS_ANSWER: str = "Напишите название темы для добавления"
ADD_TOPIC_SUCCESS_ADDED: str = "Добавлена"
ADD_TOPIC_SUCCESS_DELAYED: str = "Отложено на 1 день"
ADD_TOPIC_SUCCESS_STAGED: str = "Успешно повторили"
SHOW_ACTIVE_TOPICS_BUTTON_NAME: str  = "Show active topics"
START_MESSAGE: str  = "Choose an action"

#init bot
bot = telebot.TeleBot(API_KEY)
api = google_sheet.GoogleSheetAPI()

"""
@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_topic_button = telebot.types.KeyboardButton(ADD_TOPIC_BUTTON_NAME)
    show_active_topics_button = telebot.types.KeyboardButton(SHOW_ACTIVE_TOPICS_BUTTON_NAME)
    markup.add(add_topic_button, show_active_topics_button)
    
    bot.send_message(message.chat.id, START_MESSAGE, reply_markup=markup)
"""
@bot.message_handler(commands=["add"])
def add_topic(message):
    api.append_topic(message.text.replace('/add ', ''), 'nikitaff')
    bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_ADDED)

@bot.message_handler(commands=["delay"])
def add_topic(message):
    api.delay_topic(message.text.replace('/delay ', ''))
    bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_DELAYED)

@bot.message_handler(commands=["stage"])
def add_topic(message):
    api.stage_topic(message.text.replace('/stage ', ''))
    bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_STAGED)

bot.polling(non_stop=True, interval=0)


