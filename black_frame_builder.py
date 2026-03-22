import logging
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.messagebox import showerror, showinfo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Dark theme palette ────────────────────────────────────────────────────────
BG         = "#1e1e2e"   # sfondo principale
BG_FRAME   = "#252535"   # sfondo frame/tab
BG_WIDGET  = "#2a2a3e"   # sfondo widget input
ACCENT     = "#89b4fa"   # blu accent
ACCENT_HOV = "#74a0e8"   # accent hover
FG         = "#cdd6f4"   # testo principale
FG_DIM     = "#6c7086"   # testo secondario
DANGER     = "#f38ba8"   # rosso (recording indicator)
BORDER     = "#313244"   # bordi


def apply_dark_theme(style: ttk.Style) -> None:
    style.theme_use("clam")
    style.configure(".",
        background=BG,
        foreground=FG,
        fieldbackground=BG_WIDGET,
        bordercolor=BORDER,
        darkcolor=BG,
        lightcolor=BG_FRAME,
        troughcolor=BG_WIDGET,
        selectbackground=ACCENT,
        selectforeground=BG,
        font=("monospace", 10),
    )
    style.configure("TFrame",     background=BG_FRAME)
    style.configure("TNotebook",  background=BG, borderwidth=0)
    style.configure("TNotebook.Tab",
        background=BG_WIDGET,
        foreground=FG_DIM,
        padding=[12, 6],
        borderwidth=0,
    )
    style.map("TNotebook.Tab",
        background=[("selected", BG_FRAME)],
        foreground=[("selected", ACCENT)],
    )
    style.configure("TLabel",     background=BG_FRAME, foreground=FG)
    style.configure("Dim.TLabel", background=BG_FRAME, foreground=FG_DIM, font=("monospace", 9))
    style.configure("TButton",
        background=ACCENT,
        foreground=BG,
        borderwidth=0,
        padding=[10, 5],
        relief="flat",
    )
    style.map("TButton",
        background=[("active", ACCENT_HOV), ("disabled", BG_WIDGET)],
        foreground=[("disabled", FG_DIM)],
    )
    style.configure("Danger.TButton", background=DANGER, foreground=BG)
    style.map("Danger.TButton",
        background=[("active", "#e07090"), ("disabled", BG_WIDGET)],
    )
    style.configure("TCombobox",
        fieldbackground=BG_WIDGET,
        background=BG_WIDGET,
        foreground=FG,
        arrowcolor=ACCENT,
        borderwidth=1,
        relief="flat",
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", BG_WIDGET)],
        foreground=[("readonly", FG)],
    )
    style.configure("TEntry",
        fieldbackground=BG_WIDGET,
        foreground=FG_DIM,
        borderwidth=1,
        relief="flat",
    )
    style.configure("TSeparator", background=BORDER)


class FFmpegUI:
    RESOLUTIONS = ["1920x1080", "1280x720", "640x480"]
    FPS_LIST    = ["24", "30", "60"]

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.ffmpeg_process: subprocess.Popen | None = None

        # Percorsi — inizializzati a None per i check di validazione
        self.input_file_path:  str | None = None
        self.output_file_path: str | None = None

        self._recording_dot = None
        self._blink_job     = None

        self._build_window()

    # ── Setup finestra ────────────────────────────────────────────────────────

    def _build_window(self) -> None:
        self.master.title("FFmpeg GUI")
        self.master.configure(bg=BG)
        self.master.resizable(False, False)

        style = ttk.Style()
        apply_dark_theme(style)

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self._build_conversion_tab()
        self._build_recording_tab()

    # ── Helpers UI ────────────────────────────────────────────────────────────

    def _add_label(self, frame, text, row, col=0):
        lbl = ttk.Label(frame, text=text)
        lbl.grid(row=row, column=col, padx=12, pady=6, sticky="w")
        return lbl

    def _add_button(self, frame, text, row, command, col=1, style="TButton"):
        btn = ttk.Button(frame, text=text, command=command, style=style)
        btn.grid(row=row, column=col, padx=12, pady=6, sticky="w")
        return btn

    def _add_readonly_entry(self, frame, row, col=1, width=55):
        entry = ttk.Entry(frame, state="readonly", width=width)
        entry.grid(row=row, column=col, padx=12, pady=4, sticky="ew")
        return entry

    def _set_entry_text(self, entry, text):
        entry.config(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.config(state="readonly")

    # ── Tab: File Conversion ──────────────────────────────────────────────────

    def _build_conversion_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="  File Conversion  ")
        frame.columnconfigure(1, weight=1)

        row = 0
        self._add_label(frame, "Input file:", row)
        self._add_button(frame, "Browse…", row, self._choose_input_file)

        row += 1
        self._add_label(frame, "Output file:", row)
        self._add_button(frame, "Save as…", row, self._choose_output_path)

        row += 1
        ttk.Separator(frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=8)

        row += 1
        self._add_label(frame, "Resolution:", row)
        self.resolution_var = tk.StringVar(value=self.RESOLUTIONS[0])
        ttk.Combobox(frame, textvariable=self.resolution_var,
                     values=self.RESOLUTIONS, state="readonly", width=14
                     ).grid(row=row, column=1, padx=12, pady=6, sticky="w")

        row += 1
        self._add_label(frame, "FPS:", row)
        self.fps_var = tk.StringVar(value=self.FPS_LIST[1])
        ttk.Combobox(frame, textvariable=self.fps_var,
                     values=self.FPS_LIST, state="readonly", width=14
                     ).grid(row=row, column=1, padx=12, pady=6, sticky="w")

        row += 1
        ttk.Separator(frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=8)

        row += 1
        self._add_label(frame, "Input:", row)
        self.input_file_label = self._add_readonly_entry(frame, row)

        row += 1
        self._add_label(frame, "Output:", row)
        self.output_file_label = self._add_readonly_entry(frame, row)

        row += 1
        self.convert_button = ttk.Button(
            frame, text="▶  Convert", command=self._convert, width=30)
        self.convert_button.grid(
            row=row, column=0, columnspan=2, pady=14, padx=12)

    def _choose_input_file(self) -> None:
        path = filedialog.askopenfilename(title="Select input file")
        if path:
            self.input_file_path = path
            self._set_entry_text(self.input_file_label, path)
            logger.info("Input selezionato: %s", path)

    def _choose_output_path(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save output as",
            defaultextension=".mp4",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv")],
        )
        if path:
            self.output_file_path = path
            self._set_entry_text(self.output_file_label, path)
            logger.info("Output selezionato: %s", path)

    def _convert(self) -> None:
        # ── BUG FIX: check su None, non su hasattr ────────────────────────────
        if not self.input_file_path:
            showerror("Errore", "Seleziona prima un file di input.")
            return
        if not self.output_file_path:
            showerror("Errore", "Seleziona prima un percorso di output.")
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
        self.convert_button.config(state="disabled", text="⏳ Converting…")
        self.master.update_idletasks()

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                logger.info("Conversione completata.")
                showinfo("Completato", f"File salvato in:\n{self.output_file_path}")
            else:
                logger.error("FFmpeg error:\n%s", result.stderr)
                showerror("Errore FFmpeg", result.stderr[-800:])
        except FileNotFoundError:
            showerror("FFmpeg non trovato",
                      "FFmpeg non è installato o non è nel PATH.\n"
                      "Installalo con: sudo pacman -S ffmpeg")
        finally:
            self.convert_button.config(state="normal", text="▶  Convert")

    # ── Tab: Screen Capture (X11) ─────────────────────────────────────────────

    def _build_recording_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="  Screen Capture  ")

        indicator_frame = tk.Frame(frame, bg=BG_FRAME)
        indicator_frame.pack(pady=(20, 6))

        self.recording_canvas = tk.Canvas(
            indicator_frame, width=16, height=16,
            bg=BG_FRAME, highlightthickness=0)
        self.recording_canvas.pack(side="left", padx=(0, 8))

        self.recording_status_label = ttk.Label(
            indicator_frame, text="Pronto", style="Dim.TLabel")
        self.recording_status_label.pack(side="left")

        ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=20, pady=12)

        self.start_button = ttk.Button(
            frame, text="⏺  Start Recording",
            command=self._start_recording, width=28)
        self.start_button.pack(pady=6)

        self.stop_button = ttk.Button(
            frame, text="⏹  Stop",
            command=self._stop_recording,
            style="Danger.TButton", width=28)
        self.stop_button.pack(pady=6)
        self.stop_button.config(state="disabled")

    def _start_recording(self) -> None:
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
            showerror("FFmpeg non trovato",
                      "FFmpeg non è installato o non è nel PATH.\n"
                      "Installalo con: sudo pacman -S ffmpeg")
            return

        logger.info("Registrazione avviata → %s", output_path)

        self._recording_dot = self.recording_canvas.create_oval(
            2, 2, 14, 14, fill=DANGER, outline="")
        self._blink_dot()

        self.recording_status_label.config(text="● Registrazione in corso…", foreground=DANGER)
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

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
        self.recording_status_label.config(text="Pronto", foreground=FG_DIM)

        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def _blink_dot(self) -> None:
        """Fa lampeggiare il pallino rosso durante la registrazione."""
        if self._recording_dot is None:
            return
        current = self.recording_canvas.itemcget(self._recording_dot, "fill")
        next_color = BG_FRAME if current == DANGER else DANGER
        self.recording_canvas.itemconfig(self._recording_dot, fill=next_color)
        self._blink_job = self.master.after(600, self._blink_dot)
