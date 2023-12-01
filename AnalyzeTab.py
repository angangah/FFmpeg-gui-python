from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QTextBrowser, QFormLayout, QFileDialog, QVBoxLayout, \
    QMessageBox
import subprocess


class AnalyzeTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.video_label = QLabel("Select file:")
        self.video_button = QPushButton("Select")
        self.video_button.clicked.connect(self.browse_video)
        layout.addWidget(self.video_label)
        layout.addWidget(self.video_button)

        self.output_label = QLabel("File details:")
        self.output_browser = QTextBrowser()
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_browser)

        self.setLayout(layout)

    def browse_video(self):
        video_file, _ = QFileDialog.getOpenFileName(self, "Video selection", "",
                                                    "Video files (*.mp4 *.avi);;All Files (*)")
        if video_file:
            self.video_label.setText(f"Video selected: {video_file}")
            cmd = ["ffprobe", video_file]

            try:
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
                formatted_output = self.format_output(output)
                self.output_browser.setPlainText(formatted_output)
            except subprocess.CalledProcessError as e:
                self.show_message("Error", f"Error during video analysis: {e}")

    def format_output(self, raw_output):
        start_index = raw_output.find("Input")
        return raw_output[start_index + len("Input"):].strip()

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)