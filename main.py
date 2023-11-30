import tkinter as tk
from ffmpeg_ui import FFmpegUI

# Crea l'istanza della GUI
root = tk.Tk()
ffmpeg_gui = FFmpegUI(root)

# Avvia il loop principale della GUI
root.mainloop()