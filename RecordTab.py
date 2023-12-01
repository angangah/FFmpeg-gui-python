from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget, QPushButton, QFormLayout, QFileDialog, QMessageBox, QLabel
import subprocess


class RecordTab(QWidget):
    def __init__(self, main_app):
        super().__init__()

        self.record_process = None
        self.recording = False
        self.main_app = main_app
        layout = QFormLayout()

        self.rec_label = QLabel("REC", self)
        self.rec_label.setAlignment(Qt.AlignCenter)
        self.rec_label.setStyleSheet("QLabel { background-color : red; color : white; font-size: 20px; }")
        self.rec_label.setFixedSize(50, 50)
        self.rec_label.hide()
        layout.addWidget(self.rec_label)

        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.start_screen_recording)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addRow(self.record_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_screen_recording)
        self.stop_button.setEnabled(False)
        layout.addRow(self.stop_button)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rec_label)

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.timer.start(500)
        else:
            self.timer.stop()

        self.update_rec_label()

    def update_rec_label(self):
        self.rec_label.setVisible(self.recording)

    def paintEvent(self, event):
        if self.recording:
            painter = QPainter(self)
            painter.setPen(QColor(Qt.red))
            painter.drawRect(self.rec_label.x(), self.rec_label.y(), self.rec_label.width(), self.rec_label.height())
            painter.end()

    def resizeEvent(self, event):
        self.rec_label.move(self.width() - self.rec_label.width() - 10, 10)

    def start_screen_recording(self):
        output_path, _ = QFileDialog.getSaveFileName(self, "Output path", "",
                                                     "Video files (*.mp4);;All Files (*)")
        if output_path:
            cmd = [
                "ffmpeg",
                # source, xorg x11 for screencapture
                "-f", "x11grab",
                # resolution
                "-video_size", "1920x1080",
                # fps
                "-r", "60",
                "-i", f":0.0+0,0",
                # audio format
                "-f", "alsa",
                # audio default device
                "-i", "default",
                # codec video
                "-c:v", "libx264",
                # codec audio
                "-c:a", "aac",
                # mandatory for aac
                "-strict", "experimental",
                # output name
                output_path+".mp4"
            ]

            self.record_process = subprocess.Popen(cmd)
            self.show_message("Completed", "Screen capture in progress.")
            self.record_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            self.main_app.central_widget.setCurrentIndex(1)

    def stop_screen_recording(self):
        if hasattr(self, 'record_process'):
            self.record_process.terminate()
            self.show_message("Completed", "Screen capture aborted.")
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)

            self.main_app.central_widget.setCurrentIndex(1)
            self.recording = not self.recording

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)
