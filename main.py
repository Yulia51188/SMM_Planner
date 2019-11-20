from __future__ import print_function
import pickle
from urllib.parse import urlparse, parse_qs
import httplib2
from dotenv import load_dotenv
import smm_posting
from datetime import datetime
from time import sleep
import argparse
import os
import re
import warnings
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.auth.exceptions
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

DAYS_OF_WEAK = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье',
}


def parse_arguments():
    parser = argparse.ArgumentParser(description='Sheduled SMM posting')
    parser.add_argument('--sleep_time', '-s', type=int, default=5,
        help='Sleep time between shedule check')
    return parser.parse_args()


def get_id_from_google_sheet_formula(string):
    if not '"'in string:
        return
    url = string.split('"')[1]  
    parsed_url = urlparse(url)
    if parsed_url.query is not '': 
        query_dict = parse_qs(parsed_url.query)
        document_id = query_dict.get("id")
        if document_id:
            return document_id[0]


def update_value_in_spreadsheet(service, string, cells_range, spreadsheet_id):
    body = {
        'values': [[string]]
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range=cells_range,
        valueInputOption='RAW', 
        body=body
    ).execute()


def download_image_and_text(gauth, image_data, text_data, folder):
    image_id = get_id_from_google_sheet_formula(image_data)
    drive = GoogleDrive(gauth)
    os.makedirs(folder, exist_ok=True)
    if image_id:
        image_file_obj = drive.CreateFile({"id": image_id})
        image_file_obj.GetContentFile(
            f"{os.path.join(folder, image_file_obj['title'])}"
        )
        image_file_path = f"{folder}/{image_file_obj['title']}"

    text_id = get_id_from_google_sheet_formula(text_data)
    if text_id:
        text_file_obj = drive.CreateFile({"id": text_id})
        text_file_obj.GetContentFile(
            f"{folder}/{text_file_obj['title']}",
            'text/plain'
        )
        text_file_path = f"{folder}/{text_file_obj['title']}"
    return (image_file_path, text_file_path)


def convert_word_to_bool(string, yes_words = ('yes', '+', 'да'), 
    no_words = ('no', '-', 'нет')):     
    if string.lower() in yes_words:
        return True
    if string.lower() in no_words: 
        return False
    raise ValueError (f'Unrecognized string: {string}')


def is_time_to_publish(day, time, is_done, weekdays):
    try:
        if convert_word_to_bool(is_done):
            return 
    except ValueError:
        return
    now = datetime.now()    
    current_weekday = weekdays.get(now.weekday())
    if not current_weekday:
        raise ValueError("Wrong argument 'weekdays', can't convert current "
            "date")
    return current_weekday.lower() == day.lower() and now.hour == time 


def clear_creds_file(credentials_filename="mycreds.json"):
    if os.path.exists(credentials_filename):
        os.remove(credentials_filename)


def auth_to_google_drive(credentials_filename="mycreds.json"):
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(credentials_filename)
    if gauth.credentials is None or gauth.access_token_expired:
        gauth.LocalWebserverAuth()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile(credentials_filename)
    return gauth


def parse_is_need_to_post(string):
    try:
        is_need_to_post =convert_word_to_bool(string)
    except ValueError:
        is_need_to_post = False
    return is_need_to_post


def download_and_post(gauth, service, spreadsheet_id, value, status_cell_name,
    vk_keys, telegram_keys, fb_keys, done_label='да', 
    error_label='ошибка!'):
    
    (done_vk, done_telegram, done_fb, day, time, text_data, \
        image_data, is_done) = value
    image_file_path, text_file_path = download_image_and_text(
        gauth, 
        image_data, 
        text_data, 
        day
    )
    if not image_file_path or not text_file_path:
        raise IOError(f"Can't download files: {image_data}, {text_data}")
    posting_errors = smm_posting.post_in_socials(
        text_file_path,
        image_file_path,         
        parse_is_need_to_post(done_vk), 
        parse_is_need_to_post(done_telegram), 
        parse_is_need_to_post(done_fb),
        vk_keys.get('vk_token'),
        vk_keys.get('vk_group_id'), 
        vk_keys.get('vk_album_id'),
        telegram_keys.get('telegram_bot_token'), 
        telegram_keys.get('telegram_chat_id'), 
        fb_keys.get('fb_app_token'), 
        fb_keys.get('fb_group_id')
    )
    if any(posting_errors):
        update_value_in_spreadsheet(
            service, 
            error_label, 
            status_cell_name,
            spreadsheet_id
        )  
        error_message_list = [error for error in posting_errors if error]
        warnings.warn(f"Cell {status_cell_name}: {error_message_list}")
        return False        
    else:    
        update_value_in_spreadsheet(
            service, 
            done_label, 
            status_cell_name,
            spreadsheet_id
        )
        return True


def publish_sheduled_post(service, sheet, gauth, vk_keys, telegram_keys, 
    fb_keys, spreadsheet_id, range_name, status_column_index='H', 
    status_row_start_index=3):
    """ Thus function load values from google spreadsheet table, then check if
    it is time to publish post and try to do it. 
    The result is tuple (index, result, time), where 
    - index is None if no data was loaded from table or row index of published
    post;
    - result (type bool), True if post published as sheduled or get values from
    table but no post should be published at current time, False if any 
    error occured;
    - time is current time of posting  """
    values = get_values_from_spreadsheet(service, sheet, spreadsheet_id, 
        range_name)
    if not values:
        return (None, False, datetime.now()) 
    for value_index, value in enumerate(values):                  
        (is_vk, is_telegram, is_fb, day, time, text_data, \
        image_data, is_done) = value
        if is_time_to_publish(day, time, is_done, DAYS_OF_WEAK):            
            status_row_index = status_row_start_index + value_index
            status_cell_name = f"{status_column_index}{status_row_index}"
            result = download_and_post(gauth, service, spreadsheet_id, 
                value, status_cell_name, vk_keys, telegram_keys, fb_keys)
            return (status_row_index, result, datetime.now()) 
    return (None, True, datetime.now()) 
    

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
    args = parse_arguments()
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
    try:
        service, sheet = auth_to_google_spreadsheet()
        gauth = auth_to_google_drive()
    except (google.auth.exceptions.TransportError, \
            httplib2.ServerNotFoundError) as error:
        exit(f"Connection error, authentification failed:\n{error}")
    except google.auth.exceptions.GoogleAuthError as error:
        exit(f"Authentification error:\n{error}")
    while True:
        post_index, posting_result, posting_time = publish_sheduled_post(
            service, 
            sheet, 
            gauth, 
            vk_keys, 
            telegram_keys, 
            fb_keys, 
            spreadsheet_id, 
            range_name
        )
        if not post_index and not posting_result: 
            warnings.warn(f"No data loaded at {post_time}")
        elif post_index and posting_result:
            print(f"Post {post_index} is published successfully at "
                f"{posting_time}")
        elif post_index and not posting_result:
            warnings.warn("Some errors occured while publishing post "
                f"{post_index} at {posting_time}")
        sleep(args.sleep_time) 


if __name__ == '__main__':
    main()