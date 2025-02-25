import yt_dlp
from tqdm import tqdm

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', None)
        downloaded = d.get('downloaded_bytes', None)
        if total:
            percentage = (downloaded / total) * 100
            print(f"Downloading: {percentage:.2f}%")
            
def download_video(url):
    try:
        ydl_opts = {
            'format': 'best',  
            'outtmpl': '%(title)s.%(ext)s',  
            'progress_hooks': [progress_hook],  
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Download completed: {url}")

    except Exception as e:
        print(f"An error occurred while downloading {url}: {e}")

def download_videos(url_list):
    for url in url_list:
        download_video(url)
