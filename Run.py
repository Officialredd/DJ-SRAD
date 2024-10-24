import os
import time
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from pytube import YouTube
from pytube import Playlist
from sclib import SoundcloudAPI
import yt_dlp

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'song-request-425423-14001f775cc3.json'  # Replace with your service account file

# The ID and range of the spreadsheet.
SAMPLE_SPREADSHEET_ID = '1YuGRwT2pCXsY2YhrjLOhLkLWAEGttl4neh0kyUgT5qI'  # Replace with your Google Sheet ID
SAMPLE_RANGE_NAME = 'Sheet1!A2:D'  # Adjust range if necessary

def get_form_responses():
    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        return values
    except HttpError as err:
        print(err)
        return []
def download_youtube(youtube_url, download_folder, format_preference='mp3'):
    try:
        # Define format-specific options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_preference,  # Set to either 'mp3' or 'wav'
                'preferredquality': '320',
            }],
            'noplaylist': True,  # Ensure we only download a single track
            'ffmpeg_location': 'C:/ffmpeg/bin/ffmpeg.exe',  # Adjust if ffmpeg is installed elsewhere
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        print(f'Successfully downloaded: {youtube_url} as {format_preference}')

    except Exception as e:
        print(f'Error downloading {youtube_url}: {e}')


def download_soundcloud(track_url, download_folder):
    try:
        # Create SoundcloudAPI instance
        api = SoundcloudAPI()

        # Resolve track URL
        track = api.resolve(track_url)

        # Construct filename
        filename = os.path.join(download_folder, f'{track.artist} - {track.title}.mp3')

        # Download track as MP3
        with open(filename, 'wb+') as file:
            track.write_mp3_to(file)

        print(f'Successfully downloaded SoundCloud track: {track_url}')
    except Exception as e:
        print(f'Error downloading {track_url}: {e}')

def main():
    download_folder = 'downloads'  # Replace with your download folder path
    os.makedirs(download_folder, exist_ok=True)
    processed_urls = set()

    while True:
        responses = get_form_responses()
        for response in responses:
            if not response:
                continue
            url = response[0]
            if url not in processed_urls:
                processed_urls.add(url)
                if 'youtube.com' in url or 'youtu.be' in url:
                    download_youtube(url, download_folder)
                elif 'soundcloud.com' in url:
                    download_soundcloud(url, download_folder)
                else:
                    print(f'Unsupported URL: {url}')
        time.sleep(10)  # Check for new submissions every minute

if __name__ == '__main__':
    main()
