from __future__ import print_function
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
import smm_posting

from datetime import datetime
from time import sleep


# import argparse
# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.

SLEEP_TIME = 10

DAYS_OF_WEAK = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресение',
}


def get_id_from_google_sheet_formula(string):
    url = string.split('"')[1]  
    parsed_url = urlparse(url)
    if parsed_url.query is not '': 
        query_dict = parse_qs(parsed_url.query)
        id = query_dict.get("id")
        if id:
            return id[0]


def update_value_in_spreadsheet(service, values, cells_range, spreadsheet_id):
    body = {
        'values': [values]
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range=cells_range,
        valueInputOption='RAW', 
        body=body
    ).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))


def download_image_and_text(drive, image_data, text_data, folder):
#The column number starts at 0    
    image_id = get_id_from_google_sheet_formula(image_data)
    if not os.path.exists(f'{folder}/'):
        os.mkdir(folder)
    if image_id:
        image_file_obj = drive.CreateFile({"id": image_id})
        image_file_obj.GetContentFile(f"{folder}/{image_file_obj['title']}")
        image_file_path = f"{folder}/{image_file_obj['title']}"

    text_id = get_id_from_google_sheet_formula(text_data)
    if text_id:
        text_file_obj = drive.CreateFile({"id": text_id})
        text_file_obj.GetContentFile(
            f"{folder}/{text_file_obj['title']}",
            'text/plain'
        )
        text_file_path = f"{folder}/{text_file_obj['title']}"
    return {"image":image_file_path, "text":text_file_path}


def convert_word_to_bool(string, yes_words = ('yes', '+', 'да'), 
    no_words = ('no', '-', 'нет')):     
    if string.lower() in yes_words:
        return True
    if string.lower() in no_words: 
        return False
    raise ValueError (f'Unrecognized string: {string}')


def is_time_to_publish(day, time, is_done, weekdays):
    if convert_word_to_bool(is_done):
        return False
    now = datetime.now()    
    current_weekday = weekdays.get(now.weekday())
    if current_weekday is None:
        raise ValueError("Wrong argument weekdays, can't convert current date")
    if current_weekday.lower() == day.lower() and now.hour == time: 
        print(f'Today: {current_weekday}, {now.hour}, {time}')
        return True
    return False


def auth_to_google_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() 
    drive = GoogleDrive(gauth)
    return (drive)


def publish_post_sheduled(vk_keys, telegram_keys, fb_keys, spreadsheet_id, 
    range_name):
    service, sheet = auth_to_google_spreadsheet()
    print('Done auth to spreadsheet')
    values = get_values_from_spreadsheet(service, sheet, spreadsheet_id, 
    range_name)
    drive = auth_to_google_drive()
    print('Done auth to drive')
    status_column_index = 'H'
    status_row_start_index = 3
    done_value = ['да']
    while True:
        values = get_values_from_spreadsheet(service, sheet, spreadsheet_id, 
            range_name)
        if not values:
            print('NO DATA')
            continue
        for value_index, (is_vk, is_telegram, is_fb, day, time, text_data, \
            image_data, is_done) in enumerate(values):                  
            if is_time_to_publish(day, time, is_done, DAYS_OF_WEAK):
                print(day, convert_word_to_bool(is_done))
                downloaded_files = download_image_and_text(
                    drive, 
                    image_data, 
                    text_data, 
                    day
                )
                post_results = list(smm_posting.post_in_socials(
                    downloaded_files.get("text"),
                    downloaded_files.get("image"),
                    convert_word_to_bool(is_vk), 
                    convert_word_to_bool(is_telegram), 
                    convert_word_to_bool(is_fb),
                    vk_keys.get('vk_token'),
                    vk_keys.get('vk_group_id'), 
                    vk_keys.get('vk_album_id'),
                    telegram_keys.get('telegram_bot_token'), 
                    telegram_keys.get('telegram_chat_id'), 
                    fb_keys.get('fb_app_token'), 
                    fb_keys.get('fb_group_id')
                ))
                for result in post_results:
                    print(result)
                status_row_index = status_row_start_index + value_index
                print(f"Update cell: {status_column_index}{status_row_index}")
                update_value_in_spreadsheet(
                    service, 
                    done_value, 
                    f"{status_column_index}{status_row_index}", 
                    spreadsheet_id
                )
        print('Sleeping...')
        sleep(SLEEP_TIME)
        print('Hi!')
        

def auth_to_google_spreadsheet(token_filename='token.pickle', 
    creds_filename='credentials.json', 
    scopes='https://www.googleapis.com/auth/spreadsheets'):
    creds = None
    if os.path.exists(token_filename):
        with open(token_filename, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_filename, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_filename, 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    return (service, sheet)


def get_values_from_spreadsheet(service, sheet, spreadsheet_id, range_name):
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name, 
        valueRenderOption='FORMULA'
    ).execute()
    values = result.get('values', [])
    return values 


def main():
    load_dotenv()
    vk_keys = {
        'vk_token': os.getenv("VK_ACCESS_TOKEN"),
        'vk_group_id': os.getenv("VK_GROUP_ID"),
        'vk_album_id': os.getenv("VK_ALBUM_ID")
    }
    telegram_keys = {
        'telegram_bot_token': os.getenv("TELEGRAM_BOT_TOKEN"),
        'telegram_chat_id': os.getenv("TELEGRAM_CHANNEL_ID")
    }
    fb_keys = {
        'fb_app_token': os.getenv("FB_APP_TOKEN"),
        'fb_group_id': os.getenv("FB_GROUP_ID")
    }
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    range_name = os.getenv('RANGE_NAME')
    publish_post_sheduled(vk_keys, telegram_keys, fb_keys, spreadsheet_id, 
        range_name)


    
                      
        



if __name__ == '__main__':
    main()