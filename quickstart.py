from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

drive = GoogleDrive(gauth)

# file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
# file1.SetContentString('Hello World!') # Set content of the file from given string.
# file1.Upload()
#Auto-iterate through all files that matches this query
# file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
# for file1 in file_list:
#     print('title: %s, id: %s' % (file1['title'], file1['id']))
table_url = "https://drive.google.com/open?id=1cFbpyL4MeptrJ2ZxbT2zwYt5EdpF9SXYBQwE77ePK7g"
image_url = "1yKE3DsV3ya0YzTpWDKH4sUxPo_4BMauB"

# Initialize GoogleDriveFile instance with file id.
image_file_obj = drive.CreateFile({'id': image_url})
image_file_obj.GetContentFile('cats.jpg') # Download file as 'catlove.png'.
# table_file_obj = drive.CreateFile({'id': table_url})
# table_file_obj.GetContentFile('table.xlsx') # Download file as 'catlove.png'.

print("Done")


