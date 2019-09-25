from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
import smm_posting


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '17r4QRW_m0clut772bRnUL-U1-JiazImiZMm43SkgS9Q'
SAMPLE_RANGE_NAME = 'Лист1!A3:H14'



def get_id_from_google_sheet_formula(string):
    url = string.split('"')[1]  
    parsed_url = urlparse(url)
    if parsed_url.query is not '': 
        query_dict = parse_qs(parsed_url.query)
        id = query_dict.get("id")
        if id:
            return id[0]


def download_image_and_text(drive, image_data, text_data, folder):
#The column number starts at 0    
    image_id = get_id_from_google_sheet_formula(image_data)
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


def main():
    load_dotenv()
    vk_token = os.getenv("VK_ACCESS_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")
    vk_album_id = os.getenv("VK_ALBUM_ID")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHANNEL_ID")
    fb_app_token = os.getenv("FB_APP_TOKEN")
    fb_group_id = os.getenv("FB_GROUP_ID")



    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME, 
        valueRenderOption='FORMULA'
    ).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        # print('Name, Major:')
        # for row in values:
        #     # Print columns A and E, which correspond to indices 0 and 4.
        #     # print('%s, %s' % (row[0], row[4]))
        #     print(row)
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth() 
        drive = GoogleDrive(gauth)
        for is_vk, is_telegram, is_fb, day, time, text_data, image_data, is_done in values:      
            print(day, is_done)
            if day == "суббота" and is_done == "нет":
                downloaded_files = download_image_and_text(
                    drive, 
                    image_data, 
                    text_data, 
                    "Saturday"
                )
                post_results = list(smm_posting.post_in_socials(
                    downloaded_files.get("text"),
                    downloaded_files.get("image"),
                    vk_token,
                    vk_group_id, 
                    vk_album_id,
                    telegram_bot_token, 
                    telegram_chat_id, 
                    fb_app_token, 
                    fb_group_id
                ))
                for result in post_results:
                    print(result)
                      
        



if __name__ == '__main__':
    main()