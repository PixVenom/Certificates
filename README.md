
# Google Drive File Sync Script

This script automatically syncs a local folder with a specified Google Drive folder. It monitors the local directory for any file changes (creation, deletion, or modification) and reflects those changes in Google Drive. It also ensures that duplicate files are not uploaded again.

## Features
- **Automatic File Syncing**: Uploads new or modified files from the local folder to Google Drive.
- **Duplicate File Check**: Skips uploading files that already exist in the Google Drive folder.
- **File Deletion**: Deletes files from Google Drive when they are removed from the local folder.
- **Real-Time Monitoring**: Uses the `watchdog` library to monitor changes in the local folder.

## Requirements

- Python 3.x
- Google Cloud API credentials (Service Account Key)
- Required Python libraries

### Install the Required Libraries

Before running the script, you need to install the required Python libraries. You can install them using the following commands:

```bash
pip install --upgrade google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib watchdog
```

Alternatively, if you’re using a specific version of Python:

```bash
/path/to/your/python3 -m pip install --upgrade google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib watchdog
```

## Setup

1. **Google Cloud API Setup**:
    - Go to the Google Cloud Console: [https://console.cloud.google.com/](https://console.cloud.google.com/).
    - Create a project or use an existing one.
    - Enable the **Google Drive API** for the project.
    - Create a **Service Account** and generate a **JSON key** for the service account.
    - Download the key file and place it in your project folder.
    - Share your Google Drive folder with the service account email.

2. **Update Script**:
    - Replace the path to your service account key in the script:
    ```python
    gcp_credentials_path = "/path/to/your/service_account_key.json"
    ```
    - Replace the `drive_folder_id` with the ID of your Google Drive folder. You can get this from the folder's URL (the long string after `/folders/`):
    ```python
    drive_folder_id = "your_drive_folder_id"
    ```
    - Set the local folder path you want to sync:
    ```python
    local_folder_path = "/path/to/your/local/folder"
    ```

## Usage

1. Run the script:
    ```bash
    python script_name.py
    ```

2. The script will continuously monitor the local folder for any changes (file creation, deletion, or modification) and sync them to Google Drive.

3. Press `Ctrl + C` to stop the script at any time.

## Example

```bash
python sync_files.py
```

This will start the script and begin monitoring the folder defined in `local_folder_path`. Any changes made to files in that folder will be reflected on Google Drive.

## Troubleshooting

- **ModuleNotFoundError**: If you get an error about missing modules, ensure you’ve installed all the required packages by running:
    ```bash
    pip install --upgrade google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib watchdog
    ```

- **Permission Issues**: Ensure the service account has the necessary permissions to access and modify files in your Google Drive folder. Share the folder with the service account email.

- **Invalid Folder ID**: Ensure the `drive_folder_id` is correctly set to the folder's ID (you can get it from the folder's URL).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
