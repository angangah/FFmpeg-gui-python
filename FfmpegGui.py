import sys

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QApplication

from RecordTab import RecordTab
from ConvertTab import ConvertTab
from AnalyzeTab import AnalyzeTab


class FfmpegGui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FFmpeg GUI")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QTabWidget(self)
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    def init_ui(self):
        convert_tab = ConvertTab()
        self.central_widget.addTab(convert_tab, "Video Scaling")

        record_tab = RecordTab(self)
        self.central_widget.addTab(record_tab, "Screen Capture")

        analyze_tab = AnalyzeTab()
        self.central_widget.addTab(analyze_tab, "File Details")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = FfmpegGui()
    main_app.show()
    sys.exit(app.exec_())
