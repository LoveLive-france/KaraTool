import customtkinter as ctk
from tkinter import filedialog
from core.download_manager import DownloadManager

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LLFR Tools")
        self.geometry("1000x650")
        self._cards = {}
        self._manager = DownloadManager(on_update=self._schedule_update)
        self._build_ui()
        self._refresh_cookies_label()

    # appelé depuis le thread de téléchargement → délégué au thread principal
    def _schedule_update(self, item_id, status, progress):
        self.after(0, lambda: self._update_card(item_id, status, progress))

    # ---------- BUILD ----------

    def _build_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_input_bar()
        self._build_list_area()
        self._build_footer()

    def _build_header(self):
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(header, text="YouTube Downloader", font=("Arial", 24, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

    def _build_input_bar(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)

        self._url_entry = ctk.CTkEntry(frame, placeholder_text="Lien")
        self._url_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self._format_var = ctk.StringVar(value="Vidéo")
        ctk.CTkOptionMenu(frame, values=["Vidéo", "Audio"], variable=self._format_var).grid(
            row=0, column=1, padx=10
        )

    def _build_list_area(self):
        self._list_frame = ctk.CTkScrollableFrame(self)
        self._list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    def _build_footer(self):
        footer = ctk.CTkFrame(self)
        footer.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(footer, text="Ajouter", command=self._add_link).pack(side="left", padx=10)
        ctk.CTkButton(footer, text="Dossier", command=self._choose_folder).pack(side="left", padx=10)
        ctk.CTkButton(footer, text="Cookies", command=self._choose_cookies).pack(side="left", padx=10)
        ctk.CTkButton(footer, text="Vider cookies", command=self._clear_cookies).pack(side="left", padx=10)
        ctk.CTkButton(footer, text="Télécharger tout", command=self._start_download).pack(side="right", padx=10)

        self._cookies_lbl = ctk.CTkLabel(footer, text="", font=("Arial", 14, "bold"))
        self._cookies_lbl.pack(side="right", padx=10)

    # ---------- CARDS ----------

    def _create_card(self, item_id, url):
        card = ctk.CTkFrame(self._list_frame, corner_radius=12)
        card.pack(fill="x", padx=10, pady=8)

        left = ctk.CTkFrame(card)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(left, text=url, anchor="w").pack(fill="x")
        status_lbl = ctk.CTkLabel(left, text="⏳ En attente")
        status_lbl.pack(anchor="w", pady=5)

        progress = ctk.CTkProgressBar(card, width=150)
        progress.pack(side="right", padx=10)
        progress.set(0)

        self._cards[item_id] = {"status": status_lbl, "progress": progress}

    def _update_card(self, item_id, status, progress):
        card = self._cards.get(item_id)
        if not card:
            return
        card["status"].configure(text=status)
        if "✔️" in status:
            card["status"].configure(text_color="green")
        elif "❌" in status:
            card["status"].configure(text_color="red")
        elif "⬇️" in status:
            card["status"].configure(text_color="cyan")
        else:
            card["status"].configure(text_color="gray")
        card["progress"].set(progress)

    # ---------- ACTIONS ----------

    def _add_link(self):
        url = self._url_entry.get().strip()
        if not url:
            return
        item_id = self._manager.add(url, self._format_var.get())
        self._create_card(item_id, url)
        self._url_entry.delete(0, "end")

    def _choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self._manager.set_folder(folder)

    def _choose_cookies(self):
        path = filedialog.askopenfilename(filetypes=[("Cookies", "*.txt")])
        if path:
            self._manager.set_cookies(path)
        self._refresh_cookies_label()

    def _clear_cookies(self):
        self._manager.clear_cookies()
        self._refresh_cookies_label()

    def _start_download(self):
        self._manager.start()

    def _refresh_cookies_label(self):
        if self._manager.cookies_file:
            self._cookies_lbl.configure(text="● Cookies: chargés", text_color="green")
        else:
            self._cookies_lbl.configure(text="● Cookies: non chargés", text_color="red")
