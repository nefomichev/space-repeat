import os
import httplib2
import apiclient
import dotenv
import datetime

from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

#Load API KEY from secure .env file 
dotenv.load_dotenv()

class GoogleSheetAPI():
    CREDENTIALS_FILE = 'creds.json'
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    SHEET_NAME = "'Class Data'!"
    TABLE_STRUCTURE = {
        "TOPIC_NAME": "A",	
        "USER_NAME": "B",
        "CREATION_DATE": "C",
        "STAGE": "D",
        "DELAYS": "E",
        "EXPECTED_REMINDER_DATE": "F"
    }
    INITIAL_STAGE = 0
    INITIAL_DELAY = 0
    MAX_ROWS = 1000000

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

    def __init__(self) -> None:
        pass

    def append_row(self, row_values: list):
        response = GoogleSheetAPI.service.spreadsheets().values().append(
            spreadsheetId=GoogleSheetAPI.SPREADSHEET_ID,
            range = "A2:F1000000",
            valueInputOption = "USER_ENTERED",
            insertDataOption = "INSERT_ROWS",
            body = { "values": [row_values]}, # TODO Multiple Rows management
        ).execute()
        
        #index of A + 1 in -> "'Class Data'!A3:E3"
        search_index = len(GoogleSheetAPI.SHEET_NAME) + 1 
        row_index = response["updates"]["updatedRange"][search_index:].split(':')[0]

        return {'row_index': row_index}

    def update_cell(self, value: str, cell_position: str):
        response = GoogleSheetAPI.service.spreadsheets().values().update(
            spreadsheetId=GoogleSheetAPI.SPREADSHEET_ID,
            range = cell_position,
            valueInputOption = "USER_ENTERED",
            body = { "values": [[value]]},
        ).execute()

    def select(self, select_range, dim='ROWS'):
        # ROWS / COLUMNS 
        # TODO DOCSTRING а то Ксюша пристрелит (помогите +7999851670)
        response = GoogleSheetAPI.service.spreadsheets().values().get(
            spreadsheetId=GoogleSheetAPI.SPREADSHEET_ID,
            range = select_range,
            majorDimension = dim
        ).execute()
        return response['values']

    def find_rows(self, search_key, search_value):
        key = GoogleSheetAPI.TABLE_STRUCTURE[search_key]
        values = self.select(f"{key}1:{key}{GoogleSheetAPI.MAX_ROWS}", 'COLUMNS')[0]
        return [i + 1 for i, e in enumerate(values) if e == search_value]
        
    def append_topic(self, topic: str, user: str):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        result = self.append_row([ 
            topic, 
            user, 
            current_date,
            f'{GoogleSheetAPI.INITIAL_STAGE}',
            f'{GoogleSheetAPI.INITIAL_DELAY}',
        ])
        
        i: str = result['row_index']

        creation_date = GoogleSheetAPI.TABLE_STRUCTURE["CREATION_DATE"] + i
        delays = GoogleSheetAPI.TABLE_STRUCTURE["DELAYS"] + i
        reminder_date = GoogleSheetAPI.TABLE_STRUCTURE["EXPECTED_REMINDER_DATE"] + i
        stage = GoogleSheetAPI.TABLE_STRUCTURE["STAGE"] + i
        stage_delta = f"ВПР({stage}; stage_delta_dict!$A$1:$B$5; 2)"

        reminder_formula = f"={creation_date} + {stage_delta} + {delays}"
        self.update_cell(reminder_formula, reminder_date)

    def delay_topic(self, topic: str):
        # TODO поиск по двум полям !!
        # TODO для нескольких строк
        topic_index = self.find_rows("TOPIC_NAME", topic)
        if not topic_index:
            return 'Topic not found' 
        delay_column = GoogleSheetAPI.TABLE_STRUCTURE["DELAYS"]
        delay_cell = f"{delay_column}{topic_index[0]}"
        old_delay = self.select(delay_cell, "ROWS")[0][0]
        new_delay = int(old_delay) + 1
        self.update_cell(str(new_delay), delay_cell)
        return "Delay complete"

    def stage_topic(self, topic: str):
        # TODO поиск по двум полям !!
        # TODO для нескольких строк
        topic_index = self.find_rows("TOPIC_NAME", topic)
        if not topic_index:
            return 'Topic not found' 
        stage_column = GoogleSheetAPI.TABLE_STRUCTURE["STAGE"]
        stage_cell = f"{stage_column}{topic_index[0]}"
        old_stage = self.select(stage_cell, "ROWS")[0][0]
        new_stage = int(old_stage) + 1
        self.update_cell(str(new_stage), stage_cell)
        return "Stage complete"
    
    def get_topics_to_remind(self, reminder_date):
        topic_index = self.find_rows("EXPECTED_REMINDER_DATE", reminder_date)
        if not topic_index:
            return 'Topic not found'
        topic_column = GoogleSheetAPI.TABLE_STRUCTURE["TOPIC_NAME"]
        
        return [self.select(f"{topic_column}{x}")[0][0]for x in topic_index]