import sys
import os
import time
import re
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, 
    QLineEdit, QListWidget, QProgressBar, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadWorker(QThread):
    """Thread for downloading YouTube videos with yt_dlp."""
    progress = pyqtSignal(int, int)  # (video_index, progress)
    finished = pyqtSignal(int)  # (video_index)
    error = pyqtSignal(str)  # Error message

    def __init__(self, url, video_index):
        super().__init__()
        self.url = url
        self.video_index = video_index

    def run(self):
        ydl_opts = {
            'outtmpl': f'%(title)s-%(id)s.%(ext)s',  # Unique filename
            'noplaylist': True,  # Avoid downloading playlists
            'progress_hooks': [self.hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)

            time.sleep(1)  # Wait before renaming
            temp_file = f"{info_dict['title']}-{info_dict['id']}.mp4.part"
            final_file = f"{info_dict['title']}-{info_dict['id']}.mp4"

            try:
                if os.path.exists(temp_file):
                    os.rename(temp_file, final_file)
            except PermissionError:
                self.error.emit("File is in use by another process. Retry later.")

        except Exception as e:
            self.error.emit(str(e))

    def hook(self, d):
        if d['status'] == 'downloading':
            raw_percent = d.get('_percent_str', '0%')

            # Remove ANSI escape sequences
            percent_cleaned = re.sub(r'\x1b\[[0-9;]*m', '', raw_percent).strip('%')

            try:
                self.progress.emit(self.video_index, int(float(percent_cleaned)))
            except ValueError:
                print(f"Skipping invalid percentage format: {raw_percent}")  # Debugging
        elif d['status'] == 'finished':
            self.finished.emit(self.video_index)

class YouTubeDownloader(QWidget):
    """Main GUI application for downloading YouTube videos."""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.threads = []  # Store active download threads

    def initUI(self):
        layout = QVBoxLayout()

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter YouTube video URL")
        layout.addWidget(self.url_input)

        self.download_btn = QPushButton("Download", self)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self.setWindowTitle("YouTube Video Downloader")
        self.resize(500, 400)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        # Create list item with progress bar
        item = QListWidgetItem(self.list_widget)
        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, progress_bar)

        # Start the download in a separate thread
        thread = DownloadWorker(url, self.list_widget.count() - 1)
        thread.progress.connect(self.update_progress)
        thread.finished.connect(self.download_complete)
        thread.error.connect(self.show_error)  # Connect error signal to show error
        thread.start()
        self.threads.append(thread)

    def update_progress(self, video_index, progress):
        item = self.list_widget.item(video_index)
        progress_bar = self.list_widget.itemWidget(item)
        progress_bar.setValue(progress)

    def download_complete(self, video_index):
        item = self.list_widget.item(video_index)
        progress_bar = self.list_widget.itemWidget(item)
        progress_bar.setValue(100)

    def show_error(self, message):
        """Display an error message in a popup."""
        error_popup = QMessageBox(self)
        error_popup.setIcon(QMessageBox.Icon.Critical)
        error_popup.setWindowTitle("Error")
        error_popup.setText(f"An error occurred: {message}")
        error_popup.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec())
