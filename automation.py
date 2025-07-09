import os
import io
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# --- CONFIGURATION ---
GDRIVE_CREDENTIALS = "path to your file.json"
YOUTUBE_CREDENTIALS = GDRIVE_CREDENTIALS # only if the gdrive and youtube api enable on same account
GDRIVE_TOKEN = "gdrive_api.pickle"
YOUTUBE_TOKEN = "youtube_api.pickle"
GDRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
GDRIVE_FOLDER_NAME = "name"  # Folder in Google Drive where the videos are store
VIDEO_FOLDER = "videos"      # Local folder for downloaded videos

# --- AUTHENTICATION FUNCTIONS ---
def authenticate_google_drive():
    """Authenticate and return Google Drive API service."""
    creds = None
    if os.path.exists(GDRIVE_TOKEN):
        with open(GDRIVE_TOKEN, "rb") as token_file:
            creds = pickle.load(token_file)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GDRIVE_CREDENTIALS, GDRIVE_SCOPES)
            creds = flow.run_local_server(port=0)

        with open(GDRIVE_TOKEN, "wb") as token_file:
            pickle.dump(creds, token_file)

    return build("drive", "v3", credentials=creds)

def authenticate_youtube():
    """Authenticate and return YouTube API service."""
    creds = None
    if os.path.exists(YOUTUBE_TOKEN):
        with open(YOUTUBE_TOKEN, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CREDENTIALS, YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=0)

        with open(YOUTUBE_TOKEN, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

# --- GOOGLE DRIVE FUNCTIONS ---
def get_folder_id(service, folder_name):
    """Get the Google Drive folder ID by name."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    return folders[0]['id'] if folders else None

def get_files_in_folder(service, folder_name):
    """Get files inside a Google Drive folder."""
    folder_id = get_folder_id(service, folder_name)
    if not folder_id:
        print(f"❌ Folder '{folder_name}' not found.")
        return []

    query = f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

def download_files(service, folder_name):
    """Download all videos from Google Drive folder."""
    files = get_files_in_folder(service, folder_name)
    if not files:
        print(f"📂 No files found in '{folder_name}'. Nothing to download.")
        return False  

    print(f"📥 Downloading {len(files)} files from '{folder_name}'...")
    os.makedirs(VIDEO_FOLDER, exist_ok=True)  # Ensure local folder exists

    for file in files:
        file_id, file_name = file["id"], file["name"]
        request = service.files().get_media(fileId=file_id)
        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        local_path = os.path.join(VIDEO_FOLDER, file_name)
        with open(local_path, "wb") as f:
            f.write(file_data.getvalue())

        print(f"✔ Downloaded: {file_name} → {local_path}")

    print("✅ All files downloaded successfully!")
    return True  

def delete_files(service, folder_name):
    """Delete all videos from Google Drive folder after download."""
    files = get_files_in_folder(service, folder_name)
    if not files:
        print(f"📂 Folder '{folder_name}' is already empty.")
        return

    print(f"🗑 Deleting {len(files)} files from '{folder_name}'...")
    for file in files:
        service.files().delete(fileId=file["id"]).execute()
        print(f"❌ Deleted: {file['name']}")

    print("✅ All files deleted successfully!")

# --- YOUTUBE UPLOAD FUNCTIONS ---
def upload_short(youtube, file_path):
    """Upload a video as a YouTube Short and delete after upload."""
    video_name = os.path.basename(file_path).replace(".mp4", "")  
    title = video_name + " #Shorts"
    description = f"This is a YouTube Short titled: {video_name} #Shorts"

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Shorts", "YouTube", "Viral"],
                "categoryId": "22",
            },
            "status": {"privacyStatus": "public"},
        },
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading {video_name}: {int(status.progress() * 100)}%")

    print(f"✅ Upload complete: {response['id']}")

    os.remove(file_path)
    print(f"🗑 Deleted: {file_path}")

def upload_all_videos():
    """Find all videos in 'videos/' and upload to YouTube Shorts."""
    youtube = authenticate_youtube()
    if not os.path.exists(VIDEO_FOLDER):
        print(f"🚫 Folder '{VIDEO_FOLDER}' does not exist.")
        return

    videos = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(".mp4")]
    if not videos:
        print("🚫 No videos found to upload.")
        return

    for video in videos:
        video_path = os.path.join(VIDEO_FOLDER, video)
        upload_short(youtube, video_path)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    drive_service = authenticate_google_drive()

    if download_files(drive_service, GDRIVE_FOLDER_NAME):
        delete_files(drive_service, GDRIVE_FOLDER_NAME)  # Delete after successful download
        upload_all_videos()  # Upload to YouTube Shorts

