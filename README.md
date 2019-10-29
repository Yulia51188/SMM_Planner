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
Launch main.py to publish post in three social media.  
The example of launch in Ubuntu is:

```bash
$ python3 main.py text.txt image.jpg
```
The launch in Windows and OS is the same.

# Project Goals
The code is written for educational purposes on online-course for web-developers dvmn.org, module Python for SMM.
