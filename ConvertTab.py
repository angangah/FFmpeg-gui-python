import subprocess

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QFormLayout, QFileDialog, QMessageBox, QLineEdit, QComboBox


class ConvertTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QFormLayout()

        self.input_label = QLabel("Input File:")
        self.input_button = QPushButton("Select")
        self.input_button.clicked.connect(self.browse_input)
        layout.addRow(self.input_label, self.input_button)

        self.resolution_label = QLabel("Output Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1920x1080", "1280x720", "640x480"])
        layout.addRow(self.resolution_label, self.resolution_combo)

        self.fps_label = QLabel("Output FPS:")
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["60", "30", "24"])
        layout.addRow(self.fps_label, self.fps_combo)

        self.output_label = QLabel("Save to:")
        self.output_button = QPushButton("Select")
        self.output_button.clicked.connect(self.browse_output)
        layout.addRow(self.output_label, self.output_button)

        self.convert_button = QPushButton("Scale")
        self.convert_button.clicked.connect(self.convert_video)
        layout.addRow(self.convert_button)

        self.setLayout(layout)

    def browse_input(self):
        input_file, _ = QFileDialog.getOpenFileName(self, "Input File")
        if input_file:
            self.input_label.setText(f"Input File: {input_file}")

    def browse_output(self):
        output_file, _ = QFileDialog.getSaveFileName(self, "Selected Output", "",
                                                     "Video files (*.mp4);;All Files (*)")
        if output_file:
            self.output_label.setText(f"Save to: {output_file}")

    def convert_video(self):
        if "Input File:" not in self.input_label.text():
            self.show_message("Error", "Missing input file.")
            return

        # Verifica se è stato selezionato un percorso di output
        if "Save to:" not in self.output_label.text():
            self.show_message("Error", "Missing output file.")
            return

        selected_resolution = self.resolution_combo.currentText()
        selected_fps = self.fps_combo.currentText()
        input_source = self.input_label.text().replace("Input File: ", "")
        output_source = self.output_label.text().replace("Save to: ", "")

        cmd = [
            "ffmpeg",
            "-i", input_source,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-r", selected_fps,
            "-s", selected_resolution,
            output_source + ".mp4"
        ]

        try:
            subprocess.run(cmd, check=True)
            self.show_message("Completed", "Scaling completed")
        except subprocess.CalledProcessError as e:
            self.show_message("Error", f"Error during video scaling: {e}")

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)
