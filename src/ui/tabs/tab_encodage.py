import os
import customtkinter as ctk
from tkinter import filedialog
from core.encoding_manager import EncodingManager


class TabEncodeur(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.input_file = None
        self.output_folder = None
        self._manager = EncodingManager(on_update=self._schedule_update)
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        self.btn_input = ctk.CTkButton(
            self, text="Sélectionner un média (Vidéo ou Audio)", command=self._on_choose_file
        )
        self.btn_input.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.label_input = ctk.CTkLabel(self, text="Aucun fichier sélectionné")
        self.label_input.grid(row=1, column=0, pady=(0, 15))

        self.btn_output = ctk.CTkButton(
            self, text="Dossier de sortie", command=self._on_choose_folder
        )
        self.btn_output.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.label_output = ctk.CTkLabel(
            self, text="Aucun dossier sélectionné (par défaut celui du fichier)"
        )
        self.label_output.grid(row=3, column=0, pady=(0, 15))

        self.bitrate_frame = ctk.CTkFrame(self)
        self.bitrate_frame.grid_columnconfigure(0, weight=1)

        self.bitrate_label = ctk.CTkLabel(self.bitrate_frame, text="")
        self.bitrate_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        self.bitrate_entry = ctk.CTkEntry(self.bitrate_frame)
        self.bitrate_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.btn_encode = ctk.CTkButton(self, text="Encoder le média", command=self._on_encoding)
        self.btn_encode.grid(row=5, column=0, padx=20, pady=(30, 10), sticky="ew")

        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self, text="En attente...")
        self.status_label.grid(row=7, column=0, pady=(0, 20))

    def _on_choose_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Tous les médias supportés", "*.mp4 *.webm *.mkv *.mov *.mp3 *.wav *.flac *.m4a"),
                ("Fichiers Vidéo", "*.mp4 *.webm *.mkv *.mov"),
                ("Fichiers Audio", "*.mp3 *.wav *.flac *.m4a")
            ]
        )

        if path:
            self.input_file = path
            self.label_input.configure(text=path)
            
            ext = os.path.splitext(path)[1].lower()
            is_audio = ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]
            
            self.bitrate_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
            
            self.bitrate_entry.delete(0, "end")
            
            if is_audio:
                self.bitrate_label.configure(text="Bitrate Audio souhaité (kbps) (Par défaut : 256)")
                self.bitrate_entry.insert(0, "256")
            else:
                self.bitrate_label.configure(text="Bitrate Vidéo x265 souhaité (kbps) (Par défaut : 4000)")
                self.bitrate_entry.insert(0, "4000")
        else:
            if not self.input_file:
                self.bitrate_frame.grid_forget()

    def _on_choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.label_output.configure(text=folder)
            self._manager.set_folder(folder)

    def _on_encoding(self):
        if not self.input_file:
            self.status_label.configure(text="❌ Aucun fichier sélectionné")
            return

        if not self.output_folder:
            self.output_folder = os.path.dirname(self.input_file)
            self._manager.set_folder(self.output_folder)
            self.label_output.configure(text=self.output_folder)

        try:
            bitrate_val = int(self.bitrate_entry.get())
        except ValueError:
            self.status_label.configure(text="❌ Le bitrate doit être un nombre entier valide")
            return

        ext = os.path.splitext(self.input_file)[1].lower()
        is_audio = ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]

        if is_audio:
            self._manager.set_bitrate_params(audio_bitrate=bitrate_val)
        else:
            self._manager.set_bitrate_params(video_bitrate=bitrate_val)

        self._manager.add(self.input_file)
        self._manager.start()

    def _schedule_update(self, item_id, status, progress):
        self.after(0, lambda: self._update_ui(status, progress))

    def _update_ui(self, status, progress):
        self.status_label.configure(text=status)

        if progress is not None:
            self.progress.set(progress)

        if "✔️" in status:
            self.status_label.configure(text_color="green")
        elif "❌" in status:
            self.status_label.configure(text_color="red")
        elif "⏳" in status:
            self.status_label.configure(text_color="cyan")
        else:
            self.status_label.configure(text_color="gray")