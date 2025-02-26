import os
import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadWorker(QThread):
    """Thread for downloading YouTube videos with yt_dlp."""
    progress = pyqtSignal(int, int, str, str)  
    finished = pyqtSignal(int)  
    error = pyqtSignal(str)  

    def __init__(self, url, video_index, save_path):
        super().__init__()
        self.url = url
        self.video_index = video_index
        self.save_path = save_path

    def run(self):
        ydl_opts = {
            'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
            'noplaylist': True,  
            'format': 'bestvideo+bestaudio/best',  
            'progress_hooks': [self.hook],  
            'quiet': False,  
            'noprogress': False,  
            'nocolor': True,  
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])  
        except Exception as e:
            self.error.emit(str(e))

    def hook(self, d):
        """Hook function to update progress manually using downloaded bytes."""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes', 1)  
            downloaded_bytes = d.get('downloaded_bytes', 0)  
            progress = int((downloaded_bytes / total_bytes) * 100) if total_bytes > 0 else 0  

            speed = d.get('_speed_str', '0 KiB/s')
            downloaded_mb = downloaded_bytes / 1_048_576  

            print(f"[DEBUG] Progress: {progress}% | Speed: {speed} | Downloaded: {downloaded_mb:.2f} MB")

            self.progress.emit(self.video_index, progress, speed, f"{downloaded_mb:.2f} MB")

        elif d['status'] == 'finished':
            self.finished.emit(self.video_index)