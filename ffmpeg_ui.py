import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


class FFmpegUI:
    def __init__(self, main):

        self.master = main
        self.ffmpeg_process = None
        self.row = 0

        # Labels
        self.input_file_label = None
        self.output_file_label = None

        # Buttons
        self.convert_button = None
        self.output_path_button = None

        # Resolution
        self.resolutions = ["1920x1080", "1280x720", "640x480"]
        self.resolution_menu = None
        self.resolution_var = None

        # FPS
        self.fps_list = ["24", "30", "60"]
        self.fps_menu = None
        self.fps_var = None

        # Paths
        self.input_file_path = None
        self.output_path_path = None

        # Main windows setup
        main.title("FFmpeg GUI")
        style = ttk.Style()
        style.theme_use("clam")

        # Add widget Notebook for manage more tabs
        self.notebook = ttk.Notebook(main)
        self.notebook.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Adding conversion and screen capture tabs
        self.add_conversion_tab(main)
        self.add_screen_recording_tab(main)

        # Visual indicator while recording
        self.recording_indicator = tk.Canvas(main, width=20, height=20)
        self.recording_indicator.grid(row=3, column=2, padx=(10, 0), pady=5)
        self.recording_indicator_id = None

    def addLabel(self, frame, text, row):
        ttk.Label(frame, text=text).grid(row=row, column=0, padx=10, pady=5, sticky="w")

    def addButton(self, frame, text, row, command):
        ttk.Button(frame, text=text, command=command).grid(row=row, column=1, padx=10, pady=10, sticky="w")

    def increaseRow(self):
        self.row += 1

    def add_conversion_tab(self, master):
        # Frame creation
        conversion_frame = ttk.Frame(self.notebook)
        self.notebook.add(conversion_frame, text="File Conversion")

        self.increaseRow()

        self.addLabel(conversion_frame, "Input file:", self.row)
        self.addButton(conversion_frame, "Select", self.row, self.choose_input_file)

        self.increaseRow()

        self.addLabel(conversion_frame, "Select Resolution:", self.row)

        self.resolution_var = tk.StringVar(conversion_frame)
        self.resolution_var.set(self.resolutions[0])
        self.resolution_menu = ttk.Combobox(conversion_frame, textvariable=self.resolution_var, values=self.resolutions,
                                            state="readonly")
        self.resolution_menu.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.increaseRow()

        self.addLabel(conversion_frame, "Select FPS:", self.row)

        self.fps_var = tk.StringVar(conversion_frame)
        self.fps_var.set(self.fps_list[0])
        self.fps_menu = ttk.Combobox(conversion_frame, textvariable=self.fps_var, values=self.fps_list,
                                     state="readonly")
        self.fps_menu.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.increaseRow()

        self.addLabel(conversion_frame, "Output file:", self.row)

        self.output_path_button = ttk.Button(conversion_frame, text="Select", command=self.choose_output_path)
        self.output_path_button.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.increaseRow()

        ttk.Label(conversion_frame, text="Input selected:").grid(row=self.row, column=0, padx=10, pady=5, sticky="w")
        self.input_file_label = ttk.Entry(conversion_frame, state="readonly", width=60)
        self.input_file_label.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.increaseRow()

        ttk.Label(conversion_frame, text="Output selected:").grid(row=self.row, column=0, padx=10, pady=5, sticky="w")
        self.output_file_label = ttk.Entry(conversion_frame, state="readonly", width=60)
        self.output_file_label.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.increaseRow()

        self.convert_button = ttk.Button(conversion_frame, text="Convert", command=self.convert, width=80)
        self.convert_button.grid(row=self.row, column=0, columnspan=2, pady=10)

    def choose_input_file(self):
        file_path = filedialog.askopenfilename()
        print("Input:", file_path)
        self.input_file_path = file_path
        self.input_file_label.config(state="normal")
        self.input_file_label.delete(0, "end")
        self.input_file_label.insert(0, self.input_file_path)
        self.input_file_label.config(state="readonly")

    def choose_output_path(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                   filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        print(" Output:", output_path)
        self.output_path_path = output_path
        self.output_file_label.config(state="normal")
        self.output_file_label.delete(0, "end")
        self.output_file_label.insert(0, self.output_path_path)
        self.output_file_label.config(state="readonly")

    def convert(self):
        # Input check
        if not hasattr(self, 'input_file_path'):
            print("First select an input file.")
            return

        # Output check
        if not hasattr(self, 'output_path_path'):
            print("First select an output file.")
            return

        # output_format = self.video_format_selected.get()
        resolution = self.resolution_var.get()
        fps = self.fps_var.get()
        # video_codec = self.video_codec_var.get()
        # audio_codec = self.audio_codec_var.get()

        cmd = [
            "ffmpeg",
            "-i", self.input_file_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-r", fps,
            "-s", resolution,
            self.output_path_path
        ]

        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("process", process.args)
        print("Conversion completed.")

    def add_screen_recording_tab(self, master):
        # Frame creation
        recording_frame = ttk.Frame(self.notebook)
        self.notebook.add(recording_frame, text="Screen Capture")

        ttk.Button(recording_frame, text="Start Recording", command=self.start_screen_recording, width=80) \
            .grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Button(recording_frame, text="Stop", command=self.stop_screen_recording, width=80) \
            .grid(row=1, column=1, columnspan=2, pady=10)

    def start_screen_recording(self):

        cmd = [
            "ffmpeg",
            # source, xorg x11 for screencapture
            "-f", "x11grab",
            # resolution
            "-video_size", "1920x1080",
            # fps
            "-r", "60",
            "-i", f":0.0+0,0",
            # codec audio
            "-c:v", "libx264",
            # output name
            "./ffmpeg_captured.mp4"
        ]

        self.ffmpeg_process = subprocess.Popen(cmd)
        print("Start recording...")

        # Visual indicator turning red while recording
        self.recording_indicator_id = self.recording_indicator.create_oval(5, 5, 15, 15, fill="red")

    def stop_screen_recording(self):

        self.ffmpeg_process.terminate()
        print("Stopped.")

        # Turn off visual indicator
        self.recording_indicator.delete(self.recording_indicator_id )
