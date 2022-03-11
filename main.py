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


CALL_KW: str = "do_"
ADD_TOPIC_SUCCESS_ADDED: str = "Topic added"

#init bot
bot = telebot.TeleBot(API_KEY)
api = google_sheet.GoogleSheetAPI(SPREADSHEET_ID, CREDS_PATH)

topic_comands = {
    "DELAY": api.delay_topic,
    "REPEAT": api.stage_topic,
    "DELETE": lambda x: f"{x} deleted (test)"

}

@bot.message_handler(commands=["show"])
def get_topics(message):
    active_topics = api.get_all_active_topics()
    for topic in active_topics:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
        telebot.types.InlineKeyboardButton("DELAY",  callback_data=f"{CALL_KW}DELAY_{topic}"),
        telebot.types.InlineKeyboardButton("REPEAT", callback_data=f"{CALL_KW}REPEAT_{topic}"),
        telebot.types.InlineKeyboardButton("DELETE", callback_data=f"{CALL_KW}DELETE_{topic}"),
        )
        bot.send_message(message.chat.id, topic, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith(CALL_KW): #TODO change to variable
        get_action_callback(query)

def get_action_callback(query):
    bot.answer_callback_query(query.id)
    action_type, topic = query.data.strip(CALL_KW).split('_')
    topic_comands.get(action_type)(topic)
    bot.send_message(query.message.chat.id, f"{action_type} {topic}")

@bot.message_handler(commands=["add"])
def add_topic(message):
    api.append_topic(message.text.replace('/add', ''), 'nikitaff')
    bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_ADDED)

bot.polling(non_stop=True, interval=0)


