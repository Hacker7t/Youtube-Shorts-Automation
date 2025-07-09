# Google Drive to YouTube Shorts Automation

This script automates the process of downloading video files from a specified Google Drive folder, and then uploading them as YouTube Shorts. After successful download and upload, the original files are deleted from Google Drive and the local machine.

## Features

- **Google Drive Integration**: Authenticates with Google Drive to list, download, and delete video files.
- **YouTube API Integration**: Authenticates with YouTube to upload videos as Shorts.
- **Local File Management**: Downloads videos to a local folder and deletes them after successful upload.
- **Configurable**: Easily set your Google Drive folder name, credentials, and token paths.

## Prerequisites

Before running the script, ensure you have the following:

1.  **Python 3**: Installed on your system.
2.  **Google Cloud Project**: A project set up in Google Cloud Console.

## Setup Instructions

Follow these steps to configure your Google Cloud Project and set up the script:

### Step 1: Enable Google Drive and YouTube Data APIs

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/) and log in with your Google account.
2.  In the search bar at the top, search for "Google Drive API" and enable it for your project.
3.  Similarly, search for "YouTube Data API v3" and enable it.

### Step 2: Create OAuth 2.0 Client ID Credentials

1.  In the Google Cloud Console, navigate to "APIs & Services" > "Credentials" from the left-hand navigation menu.
2.  Click on "+ CREATE CREDENTIALS" and select "OAuth client ID".
3.  Choose "Web application" as the Application type.
4.  Give your OAuth client a name (e.g., "YouTube Uploader").
5.  Under "Authorized redirect URIs", add the following:
    * `http://localhost/`
    * `http://localhost:8080/`
6.  Click "Create".
7.  A pop-up will display your Client ID and Client Secret. **Download the JSON file** containing your credentials. This file will be named something like `client_secret_YOUR_CLIENT_ID.json`.

### Step 3: Place Your Credentials File

1.  Rename the downloaded JSON file to something more manageable, for example, `client_secret.json`.
2.  Place this `client_secret.json` file in the same directory as your `automation.py` script.
3.  Update the `GDRIVE_CREDENTIALS` and `YOUTUBE_CREDENTIALS` variables in the `automation.py` file to point to this JSON file. For example:
    ```python
    GDRIVE_CREDENTIALS = "client_secret.json"
    YOUTUBE_CREDENTIALS = "client_secret.json" # only if the gdrive and youtube api enable on same account
    ```

### Step 4: Configure Google Drive Folder Name

1.  In your Google Drive, create a folder where you will upload the videos you want to process. For instance, if you name your folder "MyVideos", then:
2.  Update the `GDRIVE_FOLDER_NAME` variable in the `automation.py` script:
    ```python
    GDRIVE_FOLDER_NAME = "MyVideos"  # Change this to your Google Drive folder name
    ```

### Step 5: Install Required Libraries

Open your terminal or command prompt and run the following command to install the necessary Python libraries:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
