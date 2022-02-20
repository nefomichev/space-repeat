import os
import telebot
import dotenv

#Load API KEY from secure .env file 
dotenv.load_dotenv()

# Constants
API_KEY: str  = os.getenv("API_KEY")
ADD_TOPIC_BUTTON_NAME: str = "Add new topic"
ADD_TOPIC_SUCCESS_ANSWER: str = "New topic added"
SHOW_ACTIVE_TOPICS_BUTTON_NAME: str  = "Show active topics"
START_MESSAGE: str  = "Choose an action"

#init bot
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_topic_button = telebot.types.KeyboardButton(ADD_TOPIC_BUTTON_NAME)
    show_active_topics_button = telebot.types.KeyboardButton(SHOW_ACTIVE_TOPICS_BUTTON_NAME)
    markup.add(add_topic_button, show_active_topics_button)
    
    bot.send_message(message.chat.id, START_MESSAGE, reply_markup=markup)

@bot.message_handler(content_types=["text"])
def add_topic(message):
    if message.text == ADD_TOPIC_BUTTON_NAME:
        bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_ANSWER)

bot.polling(non_stop=True, interval=0)


