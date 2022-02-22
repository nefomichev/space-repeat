import os
import httplib2
import apiclient
import datetime

from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

class GoogleSheetAPI():
    
    # Constants
    CREDENTIALS_FILE = 'creds.json'
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

    def __init__(self, spreadsheet_id, keyfile_name) -> None:
        self.spreadsheet_id = spreadsheet_id

        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                            keyfile_name,
                            ['https://www.googleapis.com/auth/spreadsheets',
                            'https://www.googleapis.com/auth/drive'])
        
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http = self.httpAuth)

    def append_row(self, row_values: list):
        response = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
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
        response = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range = cell_position,
            valueInputOption = "USER_ENTERED",
            body = { "values": [[value]]},
        ).execute()

    def select(self, select_range, dim='ROWS'):
        # ROWS / COLUMNS 
        # TODO DOCSTRING а то Ксюша пристрелит (помогите +7999851670)
        response = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range = select_range,
            majorDimension = dim
        ).execute()
        print(response)
        return response['values']

    #TODO сделать метод универсальным
    def find_rows(self, search_key, search_value, search_type='e'):
        key = GoogleSheetAPI.TABLE_STRUCTURE[search_key]
        values = self.select(f"{key}1:{key}{GoogleSheetAPI.MAX_ROWS}", 'COLUMNS')[0]
        if search_type == 'e':
            return [i + 1 for i, e in enumerate(values) if e == search_value]
        if search_type == 'ne':
            return [i + 1 for i, e in enumerate(values) if e != search_value]
        
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
        new_stage = max(int(old_stage) + 1, 5) # not greater then 5 
        self.update_cell(str(new_stage), stage_cell)
        return "Stage complete"
    
    def get_topics_to_remind(self, reminder_date):
        topic_index = self.find_rows("EXPECTED_REMINDER_DATE", reminder_date)
        if not topic_index:
            return 'Topic not found'
        topic_column = GoogleSheetAPI.TABLE_STRUCTURE["TOPIC_NAME"]
        
        return [self.select(f"{topic_column}{x}")[0][0]for x in topic_index]

    def get_all_active_topics(self):
        topic_index = self.find_rows("STAGE", str(5), 'ne')
        print(topic_index)
        if not topic_index:
            return 'Topic not found'
        topic_column = GoogleSheetAPI.TABLE_STRUCTURE["TOPIC_NAME"]
        return [self.select(f"{topic_column}{x}")[0][0]for x in topic_index if x > 1] # убрали первую строчку