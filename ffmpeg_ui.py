import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


class FFmpegUI:
    def __init__(self, mainWindow):
        self.ffmpeg_process = None
        self.master = mainWindow
        mainWindow.title("FFmpeg UI")

        # Utilizza uno stile ttk per ottenere widget stilizzati
        style = ttk.Style()
        style.theme_use("clam")

        # Aggiungi il widget Notebook per gestire più tabs
        self.notebook = ttk.Notebook(mainWindow)
        self.notebook.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Primo tab per la conversione di file
        self.add_conversion_tab(mainWindow)
        self.add_screen_recording_tab(mainWindow)

        # Aggiungi un indicatore visivo per la registrazione dello schermo
        self.recording_indicator = tk.Canvas(mainWindow, width=20, height=20)
        self.recording_indicator.grid(row=3, column=2, padx=(10, 0), pady=5)
        self.recording_indicator_id = None  # ID dell'oggetto disegnato sull'indicatore

    def addLabel(self, frame, text, row):
        ttk.Label(frame, text=text).grid(row=row, column=0, padx=10, pady=5, sticky="w")

    def addButton(self, frame, text, row, command):
        # Aggiungi un pulsante per selezionare un file di input
        ttk.Button(frame, text=text, command=command).grid(row=row, column=1, padx=10, pady=10, sticky="w")

    def add_conversion_tab(self, master):
        # Creazione del frame per il primo tab
        conversion_frame = ttk.Frame(self.notebook)
        self.notebook.add(conversion_frame, text="Converti File")

        self.row = 1

        self.addLabel(conversion_frame, "Input file:", self.row)
        self.addButton(conversion_frame, "Seleziona", self.row, self.choose_input_file)

        self.row += 1

        # # Aggiungi una etichetta per selezionare il formato di output
        # self.addLabel(conversion_frame, "Seleziona Formato di Output:", self.row)
        #
        # # Aggiungi una tendina per selezionare il formato di output
        # self.video_output_formats = ["mp4", "avi", "mkv"]
        # self.video_format_selected = tk.StringVar(conversion_frame)
        # self.video_format_selected.set(self.video_output_formats[0])
        # self.video_menu = ttk.Combobox(conversion_frame, textvariable=self.video_format_selected,
        #                                values=self.video_output_formats, state="readonly")
        # self.video_menu.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")
        #
        # self.row += 1

        self.addLabel(conversion_frame, "Seleziona Risoluzione:", self.row)

        self.resolutions = ["1920x1080", "1280x720", "640x480"]
        self.resolution_var = tk.StringVar(conversion_frame)
        self.resolution_var.set(self.resolutions[0])
        self.resolution_menu = ttk.Combobox(conversion_frame, textvariable=self.resolution_var, values=self.resolutions,
                                            state="readonly")
        self.resolution_menu.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.row += 1

        # self.addLabel(conversion_frame, "Seleziona Codec Video:", self.row)
        #
        # self.video_codecs = ["libx264", "libx265", "mpeg4"]
        # self.video_codec_var = tk.StringVar(conversion_frame)
        # self.video_codec_var.set(self.video_codecs[0])
        # self.video_codec_menu = ttk.Combobox(conversion_frame, textvariable=self.video_codec_var,
        #                                      values=self.video_codecs,
        #                                      state="readonly")
        # self.video_codec_menu.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")
        #
        # self.row += 1

        # self.addLabel(conversion_frame, "Seleziona Codec Audio:", self.row)
        #
        # # Aggiungi una tendina per selezionare il codec audio
        # self.audio_codecs = ["aac", "mp3", "opus"]
        # self.audio_codec_var = tk.StringVar(conversion_frame)
        # self.audio_codec_var.set(self.audio_codecs[0])
        # self.audio_codec_menu = ttk.Combobox(conversion_frame, textvariable=self.audio_codec_var,
        #                                      values=self.audio_codecs,
        #                                      state="readonly")
        # self.audio_codec_menu.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")
        #
        # self.row += 1

        self.addLabel(conversion_frame, "Seleziona FPS:", self.row)

        self.fps_list = ["24", "30", "60"]
        self.fps_var = tk.StringVar(conversion_frame)
        self.fps_var.set(self.fps_list[0])
        self.fps_menu = ttk.Combobox(conversion_frame, textvariable=self.fps_var, values=self.fps_list, state="readonly")
        self.fps_menu.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.row += 1

        # Aggiungi una etichetta per il percorso di output
        self.addLabel(conversion_frame, "Output file:", self.row)

        # Aggiungi un pulsante per selezionare il percorso di output
        self.output_path_button = ttk.Button(conversion_frame, text="Seleziona", command=self.choose_output_path)
        self.output_path_button.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.row += 1

        # Aggiungi una etichetta per visualizzare il percorso del file di input
        ttk.Label(conversion_frame, text="File di Input:").grid(row=self.row, column=0, padx=10, pady=5, sticky="w")
        self.input_file_label = ttk.Entry(conversion_frame, state="readonly", width=60)
        self.input_file_label.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.row += 1

        # Aggiungi una etichetta per visualizzare il percorso del file di output
        ttk.Label(conversion_frame, text="File di Output:").grid(row=self.row, column=0, padx=10, pady=5, sticky="w")
        self.output_file_label = ttk.Entry(conversion_frame, state="readonly", width=60)
        self.output_file_label.grid(row=self.row, column=1, padx=10, pady=5, sticky="w")

        self.row += 1
        # Aggiungi un pulsante per eseguire la conversione
        self.convert_button = ttk.Button(conversion_frame, text="Converti", command=self.convert, width=80)
        self.convert_button.grid(row=self.row, column=0, columnspan=2, pady=10)

    def choose_input_file(self):
        file_path = filedialog.askopenfilename()
        print("File di Input:", file_path)
        self.input_file_path = file_path
        self.input_file_label.config(state="normal")
        self.input_file_label.delete(0, "end")
        self.input_file_label.insert(0, self.input_file_path)
        self.input_file_label.config(state="readonly")

    def choose_output_path(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                   filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        print("Percorso di Output:", output_path)
        self.output_path_path = output_path
        self.output_file_label.config(state="normal")
        self.output_file_label.delete(0, "end")
        self.output_file_label.insert(0, self.output_path_path)
        self.output_file_label.config(state="readonly")

    def convert(self):
        # Verifica se è stato selezionato un file di input
        if not hasattr(self, 'input_file_path'):
            print("Seleziona prima un file di input.")
            return

        # Verifica se è stato selezionato un percorso di output
        if not hasattr(self, 'output_path_path'):
            print("Seleziona prima un percorso di output.")
            return

        # Esegui il comando FFmpeg utilizzando subprocess
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

        # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # output, error = process.communicate()
        # return_code = process.returncode
        #
        # print("output", output)
        # print("error", error)
        # print("return_code", return_code)
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("process", process.args)
        print("Conversione completata.")

    def add_screen_recording_tab(self, master):
        # Creazione del frame per il secondo tab
        recording_frame = ttk.Frame(self.notebook)
        self.notebook.add(recording_frame, text="Registra Monitor")

        # Aggiungi un pulsante per avviare la registrazione del monitor
        ttk.Button(recording_frame, text="Registra", command=self.start_screen_recording, width=80) \
            .grid(row=0, column=0, columnspan=2, pady=10)

        # Aggiungi un pulsante per fermare la cattura
        ttk.Button(recording_frame, text="Stop", command=self.stop_screen_recording, width=80) \
            .grid(row=1, column=1, columnspan=2, pady=10)

    def start_screen_recording(self):

        # Esegui il comando FFmpeg per la registrazione del monitor
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
        print("Avvio registrazione in corso...")

        # Aggiorna l'indicatore visivo durante la registrazione
        self.recording_indicator_id = self.recording_indicator.create_oval(5, 5, 15, 15, fill="red")


    def stop_screen_recording(self):

        self.ffmpeg_process.terminate()
        print("Registrazione del monitor interrotta.")

        # Rimuovi l'indicatore visivo quando la registrazione è terminata
        self.recording_indicator.delete(self.recording_indicator_id)
