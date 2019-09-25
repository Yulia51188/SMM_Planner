from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth



# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '17r4QRW_m0clut772bRnUL-U1-JiazImiZMm43SkgS9Q'
SAMPLE_RANGE_NAME = 'Лист1!A3:H14'



def get_id_from_google_sheet_formula(string):
    string_parsing = string.split('"')
    base_url, id = string_parsing[1].split("=") 
    return id


def download_image_and_text(drive, image_data, text_data, folder):
#The column number starts at 0    
    image_id = get_id_from_google_sheet_formula(image_data)
    image_file_obj = drive.CreateFile({"id": image_id})
    image_file_obj.GetContentFile(f"{folder}/{image_file_obj['title']}")

    text_id = get_id_from_google_sheet_formula(text_data)
    text_file_obj = drive.CreateFile({"id": text_id})
    text_file_obj.GetContentFile(
        f"{folder}/{text_file_obj['title']}",
        'text/plain'
    )
    return True


def main():
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
                print("Нужно опубликовать")
                print(download_image_and_text(image_data, text_data, "Saturday"))      
                print(download_image_and_text(drive, image_data, text_data, "Saturday"))      
        



if __name__ == '__main__':
    main()