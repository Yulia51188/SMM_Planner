# SMM_Planner
A script posts text with image in different media: Telegram, VK, FB corresponding to a shedule as Google SpreadSheet placed in Google Drive.
The script is working in neverending loop, also if connection error happens. Posting is available in any SMM channel (VK, FB, Telegram) as pointed in the shedule table.

# How to install
The script uses enviroment file with Instagram authorization data. The file '.env' must include following data:
- VK [group id](http://regvk.com/id/) "VK_GROUP_ID", album id "VK_ALBUM_ID" and [token](https://vk.com/dev/implicit_flow_user) "VK_ACCESS_TOKEN" with following permissions: photos, groups, wall and offline. 
- Telegram Bot [token](https://smmplanner.com/blog/otlozhennyj-posting-v-telegram/) "TELEGRAM_BOT_TOKEN" and channel id "TELEGRAM_CHANNEL_ID".
- FaceBook application [marker](https://developers.facebook.com/tools/explorer/) "FB_APP_TOKEN" and group id "FB_GROUP_ID"
- Google Spreadsheets id and token ("GOOGLE_SHEET_CLIENT_ID", "GOOGLE_SHEET_CLIENT_SECRET"), Google API [quickstart](https://developers.google.com/sheets/api/quickstart/python)
- Google Drive id and token("GOOGLE_DRIVE_CLIENT_ID", "GOOGLE_DRIVE_CLIENT_SECRET"), see authentification [tutorial](https://gsuitedevs.github.io/PyDrive/docs/build/html/quickstart.html#authentication)
- Shedule table information as spreadsheet id and data cells range ("SPREADSHEET_ID", "RANGE_NAME"). See example table [here](https://docs.google.com/spreadsheets/d/17r4QRW_m0clut772bRnUL-U1-JiazImiZMm43SkgS9Q/edit#gid=0).

Python3 should be already installed. Then use pip3 (or pip) to install dependencies:

```bash
pip3 install -r requirements.txt
```

# How to launch
Launch main.py to publish post in social media corresponding to the shedule table, as table [here].  
The example of launch in Ubuntu is:
```bash
$ python3 main.py -s 5
Post 10 is published as sheduled at 2019-10-29 10:56:48.370317
```
If there are some errors while posting, you see label 'ошибка' in the table and details in UserWarning:
```bash
$ python3 main.py
main.py:157: UserWarning: Cell H5: [FBPostingError({'error': {'message': 'Error validating access token: Session has expired on Friday, 08-Nov-19 01:35:34 PST. The current time is Saturday, 16-Nov-19 13:33:59 PST.', 'type': 'OAuthException', 'code': 190, 'error_subcode': 463, 'fbtrace_id': 'ADJbY30tY_2qCW9sxzo2VRC'}},)]
```
You also can launch smm_posting.py with arguments text_file_path and image_file_path, as folowing:
```bash
$ python3 smm_posting.py среда/Обоняние среда/40df9364a4e00211880703cbf25c4351.jpg
Post is published successfully
```
The launch in Windows and OS is the same.

# Project Goals
The code is written for educational purposes on online-course for web-developers dvmn.org, module Python for SMM.
