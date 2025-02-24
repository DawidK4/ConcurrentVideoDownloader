import yt_dlp
from tqdm import tqdm

# Progress hook for showing download percentage
def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes', None)
        downloaded = d.get('downloaded_bytes', None)
        if total:
            percentage = (downloaded / total) * 100
            print(f"Downloading: {percentage:.2f}%")
            
# Download video from URL
def download_video(url):
    try:
        ydl_opts = {
            'format': 'best',  # You can adjust this for specific formats or resolutions
            'outtmpl': '%(title)s.%(ext)s',  # Save video with title as filename
            'progress_hooks': [progress_hook],  # Attach the progress hook
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Download completed: {url}")

    except Exception as e:
        print(f"An error occurred while downloading {url}: {e}")

# Batch download multiple videos
def download_videos(url_list):
    for url in url_list:
        download_video(url)

if __name__ == '__main__':
    # User input for video URLs
    video_urls = input("Enter a comma-separated list of video URLs: ").split(',')
    video_urls = [url.strip() for url in video_urls]  # Clean any extra spaces
    
    # Start downloading videos
    download_videos(video_urls)
