import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, 
    QLineEdit, QListWidget, QProgressBar, QListWidgetItem, 
    QMessageBox, QFileDialog, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal
from downloader import DownloadWorker

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