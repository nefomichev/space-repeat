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


CALL_KW: str = "do"
SPL_SYMBOL: str = "$&$"
ADD_TOPIC_SUCCESS_ADDED: str = "Topic added"
NO_TOPIC_FOUNDED: str = """There are no active topics! Add new with /add <topic_name> 
                           \nExample: /add main business metrics
                        """
INVALID_ADD_COMMAND: str = "Error! Topic name is empty, try: /add <topic_name> "
ACTIVE_TOPICS: str = """\nActive topic list. 
                        \nUse inline buttons to interact:"""


#init bot
bot = telebot.TeleBot(API_KEY)
api = google_sheet.GoogleSheetAPI(SPREADSHEET_ID, CREDS_PATH)

topic_comands = {
    "DELAY": api.delay_topic,
    "REPEAT": api.stage_topic,
    "DELETE": api.delete_topic,

}

@bot.message_handler(commands=["show"])
def get_topics(message):
    active_topics = api.get_all_active_topics()
    if active_topics:
        bot.send_message(message.chat.id, ACTIVE_TOPICS)
        for topic in active_topics:
            keyboard_row = []
            for command in topic_comands.keys():
                keyboard_row.append(telebot.types.InlineKeyboardButton(command,  callback_data=f"{CALL_KW}{SPL_SYMBOL}{command}{SPL_SYMBOL}{topic}"))
            
            keyboard = telebot.types.InlineKeyboardMarkup([keyboard_row])
            bot.send_message(message.chat.id, topic, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, NO_TOPIC_FOUNDED)

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith(CALL_KW):
        get_action_callback(query)

def get_action_callback(query):
    bot.answer_callback_query(query.id)
    action_type, topic = query.data.strip(CALL_KW+SPL_SYMBOL).split(SPL_SYMBOL)
    response = topic_comands.get(action_type)(topic)
    bot.send_message(query.message.chat.id, f"{response} - {topic}")
    get_topics(query.message)

@bot.message_handler(commands=["add"])
def add_topic(message):
    topic_name = message.text.replace('/add', '')
    if topic_name:
        api.append_topic(message.text.replace('/add', ''), 'nikitaff')
        bot.send_message(message.chat.id, ADD_TOPIC_SUCCESS_ADDED)
    else:
        bot.send_message(message.chat.id, INVALID_ADD_COMMAND)

bot.polling(non_stop=True, interval=0)