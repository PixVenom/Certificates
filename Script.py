import os
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

# --- Configuration ---
local_folder_path = "/Users/pixvenom/Desktop/CHRIST UNIVERSITY/CERTIFICATES"
gcp_credentials_path = "/Users/pixvenom/Desktop/CHRIST UNIVERSITY/CERTIFICATES/certificates-459320-d02a2b8ee89a.json"
drive_folder_id = "18LYflMmzi5T_939l9-GW_uB9JDFIwFtL"

SCOPES = ['https://www.googleapis.com/auth/drive']

def upload_to_drive(drive_service, local_file_path, drive_folder_id):
    """
    Uploads a file to Google Drive, skipping if a file with the same name already exists.
    """
    file_name = os.path.basename(local_file_path)

    # Check if a file with the same name exists in the target folder
    try:
        query = f"name = '{file_name}' and '{drive_folder_id}' in parents and trashed = false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        existing_files = results.get('files', [])

        if existing_files:
            print(f"Skipped (duplicate): {file_name} already exists in Google Drive folder.")
            return

        media = MediaFileUpload(local_file_path, resumable=True)
        file_metadata = {
            'name': file_name,
            'parents': [drive_folder_id]
        }
        file = drive_service.files().create(body=file_metadata, media=media, fields='id').execute()
        print(f"Uploaded: {file_name} to Google Drive (file ID: {file.get('id')})")

    except HttpError as error:
        print(f"An error occurred uploading {file_name}: {error}")
    except Exception as e:
        print(f"An unexpected error occurred uploading {file_name}: {e}")

def delete_from_drive(drive_service, file_name, drive_folder_id):
    """
    Deletes a file from Google Drive by name within the specified folder.
    """
    try:
        query = f"name='{file_name}' and '{drive_folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields='files(id)').execute()
        items = results.get('files', [])

        if not items:
            print(f"File {file_name} not found in Google Drive folder.")
            return

        for item in items:
            drive_service.files().delete(fileId=item['id']).execute()
            print(f"Deleted from Drive: {file_name} (ID: {item['id']})")

    except HttpError as error:
        print(f"An error occurred deleting {file_name}: {error}")
    except Exception as e:
        print(f"An unexpected error occurred deleting {file_name}: {e}")

class MyEventHandler(FileSystemEventHandler):
    """
    Handles file system events (creation, modification, deletion).
    """
    def __init__(self, drive_service, local_folder_path, drive_folder_id):
        self.drive_service = drive_service
        self.local_folder_path = local_folder_path
        self.drive_folder_id = drive_folder_id
        super().__init__()

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            upload_to_drive(self.drive_service, file_path, self.drive_folder_id)

    def on_deleted(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            delete_from_drive(self.drive_service, file_name, self.drive_folder_id)

    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            upload_to_drive(self.drive_service, file_path, self.drive_folder_id)

def main():
    if not os.path.exists(gcp_credentials_path):
        print(f"Error: Google Cloud credentials not found at {gcp_credentials_path}")
        return

    try:
        credentials = service_account.Credentials.from_service_account_file(
            gcp_credentials_path, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Failed to authenticate with Google Drive: {e}")
        return

    if not os.path.exists(local_folder_path):
        print(f"Error: Local folder not found at {local_folder_path}")
        return

    # Validate access to the Drive folder
    try:
        results = drive_service.files().list(
            q=f"'{drive_folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name)").execute()
        print(f"Connected to Google Drive folder with ID: {drive_folder_id}")
    except HttpError as error:
        print(f"Drive access error: {error}")
        return

    # --- Initial sync ---
    print("Starting initial sync of local folder to Google Drive...")
    for root, _, files in os.walk(local_folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            upload_to_drive(drive_service, file_path, drive_folder_id)

    # --- Watch for changes ---
    event_handler = MyEventHandler(drive_service, local_folder_path, drive_folder_id)
    observer = Observer()
    observer.schedule(event_handler, local_folder_path, recursive=True)
    observer.start()

    print(f"Watching for changes in: {local_folder_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping folder watcher.")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
