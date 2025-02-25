import sys
import os
import re
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, 
    QLineEdit, QListWidget, QProgressBar, QListWidgetItem, 
    QMessageBox, QFileDialog, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadWorker(QThread):
    """Thread for downloading YouTube videos with yt_dlp."""
    progress = pyqtSignal(int, int, str, str)  # (video_index, progress, speed, downloaded)
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

class YouTubeDownloader(QWidget):
    """Main GUI application for downloading YouTube videos."""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.threads = []
        self.save_path = ''

    def initUI(self):
        layout = QVBoxLayout()

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter YouTube video URL")
        layout.addWidget(self.url_input)

        self.select_path_btn = QPushButton("Select Save Path", self)
        self.select_path_btn.clicked.connect(self.select_save_path)
        layout.addWidget(self.select_path_btn)

        self.download_btn = QPushButton("Download", self)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self.setWindowTitle("YouTube Video Downloader")
        self.resize(600, 500)

    def select_save_path(self):
        """Allow the user to select a folder where videos will be saved."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.save_path = folder  

    def start_download(self):
        url = self.url_input.text().strip()
        if not url or not self.save_path:
            QMessageBox.warning(self, "Warning", "Please enter a valid URL and select a save path!")
            return
        
        item = QListWidgetItem(self.list_widget)
        widget = QWidget()
        layout = QVBoxLayout()

        title_label = QLabel("Downloading...")  
        speed_label = QLabel("Speed: 0 KiB/s")  
        downloaded_label = QLabel("Downloaded: 0 MB")  
        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)  

        layout.addWidget(title_label)
        layout.addWidget(progress_bar)
        layout.addWidget(speed_label)
        layout.addWidget(downloaded_label)

        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

        thread = DownloadWorker(url, self.list_widget.count() - 1, self.save_path)
        thread.progress.connect(self.update_progress)
        thread.finished.connect(self.download_complete)
        thread.error.connect(self.show_error)
        thread.start()
        self.threads.append(thread)

    def update_progress(self, video_index, progress, speed, downloaded):
        """Update the progress bar and labels in real time."""
        item = self.list_widget.item(video_index)
        widget = self.list_widget.itemWidget(item)

        if widget:
            labels = widget.findChildren(QLabel)
            progress_bar = widget.findChild(QProgressBar)

            labels[0].setText("Downloading...")  
            progress_bar.setValue(progress)
            labels[1].setText(f"Speed: {speed}")  
            labels[2].setText(f"Downloaded: {downloaded}")  

    def download_complete(self, video_index):
        """Update the UI when the download completes."""
        item = self.list_widget.item(video_index)
        widget = self.list_widget.itemWidget(item)

        if widget:
            labels = widget.findChildren(QLabel)
            progress_bar = widget.findChild(QProgressBar)

            labels[0].setText("Download Complete!")  
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
