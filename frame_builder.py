import logging
import signal
import subprocess
import tkinter as tk
import customtkinter as ctk

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Tema ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DANGER = "#f38ba8"


class FFmpegUI:
    RESOLUTIONS = ["1920x1080", "1280x720", "640x480"]
    FPS_LIST    = ["24", "30", "60"]

    def __init__(self, master: ctk.CTk) -> None:
        self.master = master
        self.ffmpeg_process: subprocess.Popen | None = None

        self.input_file_path:  str | None = None
        self.output_file_path: str | None = None

        self._recording_dot = None
        self._blink_job     = None
        self._blink_state   = False

        self._build_window()

    # ── Setup finestra ────────────────────────────────────────────────────────

    def _build_window(self) -> None:
        self.master.title("FFmpeg GUI")
        self.master.resizable(False, False)

        self.tabview = ctk.CTkTabview(self.master, width=580)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=16)

        self.tabview.add("File Conversion")
        self.tabview.add("Screen Capture")

        self._build_conversion_tab(self.tabview.tab("File Conversion"))
        self._build_recording_tab(self.tabview.tab("Screen Capture"))

    # ── Helpers UI ────────────────────────────────────────────────────────────

    def _label(self, parent, text, **kwargs) -> ctk.CTkLabel:
        return ctk.CTkLabel(parent, text=text, anchor="w", **kwargs)

    def _button(self, parent, text, command, width=120, fg_color=None, **kwargs) -> ctk.CTkButton:
        kw = dict(text=text, command=command, width=width)
        if fg_color:
            kw["fg_color"] = fg_color
        kw.update(kwargs)
        return ctk.CTkButton(parent, **kw)

    def _entry_readonly(self, parent, width=380) -> ctk.CTkEntry:
        e = ctk.CTkEntry(parent, width=width, state="disabled",
                         text_color=("gray60", "gray50"))
        return e

    def _set_entry(self, entry: ctk.CTkEntry, text: str) -> None:
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.configure(state="disabled")

    def _show_error(self, title: str, message: str) -> None:
        dialog = ctk.CTkToplevel(self.master)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=message, wraplength=340).pack(padx=24, pady=(20, 8))
        ctk.CTkButton(dialog, text="OK", width=80, command=dialog.destroy).pack(pady=(0, 16))

    def _show_info(self, title: str, message: str) -> None:
        dialog = ctk.CTkToplevel(self.master)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=message, wraplength=340).pack(padx=24, pady=(20, 8))
        ctk.CTkButton(dialog, text="OK", width=80, command=dialog.destroy).pack(pady=(0, 16))

    # ── Tab: File Conversion ──────────────────────────────────────────────────

    def _build_conversion_tab(self, tab) -> None:
        pad = {"padx": 12, "pady": 6}

        # Input
        row0 = ctk.CTkFrame(tab, fg_color="transparent")
        row0.pack(fill="x", **pad)
        self._label(row0, "Input file:").pack(side="left")
        self._button(row0, "Browse…", self._choose_input_file, width=100
                     ).pack(side="right")

        self.input_file_label = self._entry_readonly(tab)
        self.input_file_label.pack(fill="x", **pad)

        # Output
        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", **pad)
        self._label(row1, "Output file:").pack(side="left")
        self._button(row1, "Save as…", self._choose_output_path, width=100
                     ).pack(side="right")

        self.output_file_label = self._entry_readonly(tab)
        self.output_file_label.pack(fill="x", **pad)

        ctk.CTkFrame(tab, height=1, fg_color=("gray70", "gray30")
                     ).pack(fill="x", padx=12, pady=10)

        # Resolution + FPS
        options_frame = ctk.CTkFrame(tab, fg_color="transparent")
        options_frame.pack(fill="x", **pad)

        self._label(options_frame, "Resolution:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.resolution_var = ctk.StringVar(value=self.RESOLUTIONS[0])
        ctk.CTkOptionMenu(options_frame, variable=self.resolution_var,
                          values=self.RESOLUTIONS, width=140
                          ).grid(row=0, column=1, padx=(0, 24))

        self._label(options_frame, "FPS:").grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.fps_var = ctk.StringVar(value=self.FPS_LIST[1])
        ctk.CTkOptionMenu(options_frame, variable=self.fps_var,
                          values=self.FPS_LIST, width=80
                          ).grid(row=0, column=3)

        ctk.CTkFrame(tab, height=1, fg_color=("gray70", "gray30")
                     ).pack(fill="x", padx=12, pady=10)

        # Convert button
        self.convert_button = ctk.CTkButton(
            tab, text="▶  Convert", command=self._convert, width=200, height=38)
        self.convert_button.pack(pady=(4, 12))

    def _choose_input_file(self) -> None:
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="Select input file")
        if path:
            self.input_file_path = path
            self._set_entry(self.input_file_label, path)
            logger.info("Input selezionato: %s", path)

    def _choose_output_path(self) -> None:
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            title="Save output as",
            defaultextension=".mp4",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv")],
        )
        if path:
            self.output_file_path = path
            self._set_entry(self.output_file_label, path)
            logger.info("Output selezionato: %s", path)

    def _convert(self) -> None:
        if not self.input_file_path:
            self._show_error("Errore", "Seleziona prima un file di input.")
            return
        if not self.output_file_path:
            self._show_error("Errore", "Seleziona prima un percorso di output.")
            return

        resolution = self.resolution_var.get()
        fps        = self.fps_var.get()

        cmd = [
            "ffmpeg", "-y",
            "-i", self.input_file_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-r", fps,
            "-s", resolution,
            self.output_file_path,
        ]

        logger.info("Avvio conversione: %s", " ".join(cmd))
        self.convert_button.configure(state="disabled", text="⏳ Converting…")
        self.master.update_idletasks()

        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                logger.info("Conversione completata.")
                self._show_info("Completato", f"File salvato in:\n{self.output_file_path}")
            else:
                logger.error("FFmpeg error:\n%s", result.stderr)
                self._show_error("Errore FFmpeg", result.stderr[-400:])
        except FileNotFoundError:
            self._show_error("FFmpeg non trovato",
                             "FFmpeg non è installato o non è nel PATH.\n"
                             "Installalo con: sudo pacman -S ffmpeg")
        finally:
            self.convert_button.configure(state="normal", text="▶  Convert")

    # ── Tab: Screen Capture (X11) ─────────────────────────────────────────────

    def _build_recording_tab(self, tab) -> None:
        # Indicatore stato
        indicator_frame = ctk.CTkFrame(tab, fg_color="transparent")
        indicator_frame.pack(pady=(24, 4))

        self.recording_canvas = tk.Canvas(
            indicator_frame, width=16, height=16,
            bg="#2b2b2b", highlightthickness=0)
        self.recording_canvas.pack(side="left", padx=(0, 8))

        self.recording_status_label = ctk.CTkLabel(
            indicator_frame, text="Pronto", text_color="gray50")
        self.recording_status_label.pack(side="left")

        ctk.CTkFrame(tab, height=1, fg_color=("gray70", "gray30")
                     ).pack(fill="x", padx=12, pady=16)

        self.start_button = ctk.CTkButton(
            tab, text="⏺  Start Recording",
            command=self._start_recording, width=200, height=38)
        self.start_button.pack(pady=6)

        self.stop_button = ctk.CTkButton(
            tab, text="⏹  Stop",
            command=self._stop_recording,
            width=200, height=38,
            fg_color=DANGER, hover_color="#e07090", text_color="#1e1e2e",
            state="disabled")
        self.stop_button.pack(pady=6)

    def _start_recording(self) -> None:
        from tkinter import filedialog
        output_path = filedialog.asksaveasfilename(
            confirmoverwrite=False,
            defaultextension=".mp4",
            filetypes=[("Video files", "*.mp4")],
        )
        if not output_path:
            return

        cmd = [
            "ffmpeg",
            "-f", "x11grab",
            "-video_size", "1920x1080",
            "-r", "60",
            "-i", ":0.0+0,0",
            "-f", "alsa",
            "-i", "default",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path,
        ]

        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            self._show_error("FFmpeg non trovato",
                             "FFmpeg non è installato o non è nel PATH.\n"
                             "Installalo con: sudo pacman -S ffmpeg")
            return

        logger.info("Registrazione avviata → %s", output_path)

        self._recording_dot = self.recording_canvas.create_oval(
            2, 2, 14, 14, fill=DANGER, outline="")
        self._blink_dot()

        self.recording_status_label.configure(
            text="● Registrazione in corso…", text_color=DANGER)
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def _stop_recording(self) -> None:
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            try:
                self.ffmpeg_process.stdin.write(b"q")
                self.ffmpeg_process.stdin.flush()
                self.ffmpeg_process.wait(timeout=10)
            except Exception as exc:
                logger.warning("Errore durante l'arresto di FFmpeg: %s", exc)
                self.ffmpeg_process.terminate()

        logger.info("Registrazione fermata.")

        self._blink_job = None
        self.recording_canvas.delete("all")
        self._recording_dot = None
        self.recording_status_label.configure(text="Pronto", text_color="gray50")

        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def _blink_dot(self) -> None:
        if self._recording_dot is None:
            return
        self._blink_state = not self._blink_state
        color = DANGER if self._blink_state else "#2b2b2b"
        self.recording_canvas.itemconfig(self._recording_dot, fill=color)
        self._blink_job = self.master.after(600, self._blink_dot)
