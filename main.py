import sys
from PyQt6.QtWidgets import QApplication
from ui import YouTubeDownloader

if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec())
