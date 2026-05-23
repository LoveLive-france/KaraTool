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
            self,
            text="Sélectionner vidéo",
            command=self._on_choose_file
        )
        self.btn_input.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.label_input = ctk.CTkLabel(self, text="Aucun fichier sélectionné")
        self.label_input.grid(row=1, column=0, pady=(0, 15))

        self.btn_output = ctk.CTkButton(
            self,
            text="Dossier de sortie",
            command=self._on_choose_folder
        )
        self.btn_output.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.label_output = ctk.CTkLabel(self, text="Aucun dossier sélectionné (par défaut celui du fichier)")
        self.label_output.grid(row=3, column=0, pady=(0, 15))


        self.video_bitrate = ctk.IntVar(value=4000)

        bitrate_frame = ctk.CTkFrame(self)
        bitrate_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        bitrate_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bitrate_frame,
            text="Bitrate vidéo (kbps) (Par défaut 4000)"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        self.bitrate_entry = ctk.CTkEntry(bitrate_frame)
        self.bitrate_entry.insert(0, "4000")
        self.bitrate_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        def sync_bitrate(event=None):
            try:
                self.video_bitrate.set(int(self.bitrate_entry.get()))
            except Exception:
                pass

        self.bitrate_entry.bind("<KeyRelease>", sync_bitrate)

        self.btn_encode = ctk.CTkButton(
            self,
            text="Encoder",
            command=self._on_encoding
        )
        self.btn_encode.grid(
            row=5,
            column=0,
            padx=20,
            pady=(30, 20),
            sticky="ew"
        )

        self.status_label = ctk.CTkLabel(self, text="En attente...")
        self.status_label.grid(row=6, column=0, pady=(0, 20))

    def _on_choose_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Vidéo", "*.mp4 *.webm *.mkv *.mov")]
        )

        if path:
            self.input_file = path
            self.label_input.configure(text=path)

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
        elif "⬇️" in status or "⏳" in status:
            self.status_label.configure(text_color="cyan")
        else:
            self.status_label.configure(text_color="gray")
