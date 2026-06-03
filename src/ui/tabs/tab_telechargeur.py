import customtkinter as ctk
from tkinter import filedialog
from core.download_manager import DownloadManager


class TabTelechargeur(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._cartes = {}
        self._manager = DownloadManager(on_update=self._schedule_update)
        self._build()
        self._refresh_label_cookies()

    def _build(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_barre_saisie()
        self._build_liste()
        self._build_pied_de_page()

    def _build_header(self):
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(
            header, text="YouTube Downloader", font=("Arial", 24, "bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

    def _build_barre_saisie(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)

        self._entree_url = ctk.CTkEntry(frame, placeholder_text="Lien")
        self._entree_url.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self._format_selectionne = ctk.StringVar(value="Vidéo")
        ctk.CTkOptionMenu(
            frame, values=["Vidéo", "Audio"], variable=self._format_selectionne
        ).grid(row=0, column=1, padx=10)

    def _build_liste(self):
        self._frame_liste = ctk.CTkScrollableFrame(self)
        self._frame_liste.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    def _build_pied_de_page(self):
        pied = ctk.CTkFrame(self)
        pied.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(pied, text="Ajouter", command=self._on_ajouter_lien).pack(
            side="left", padx=10
        )
        ctk.CTkButton(pied, text="Dossier", command=self._on_choisir_dossier).pack(
            side="left", padx=10
        )
        ctk.CTkButton(pied, text="Cookies", command=self._on_choisir_cookies).pack(
            side="left", padx=10
        )
        ctk.CTkButton(pied, text="Vider cookies", command=self._on_vider_cookies).pack(
            side="left", padx=10
        )
        ctk.CTkButton(
            pied, text="Télécharger tout", command=self._on_lancer_telechargement
        ).pack(side="right", padx=10)

        self._label_cookies = ctk.CTkLabel(pied, text="", font=("Arial", 14, "bold"))
        self._label_cookies.pack(side="right", padx=10)

    def _creer_carte(self, item_id, url):
        carte = ctk.CTkFrame(self._frame_liste, corner_radius=12)
        carte.pack(fill="x", padx=10, pady=8)

        colonne_gauche = ctk.CTkFrame(carte)
        colonne_gauche.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(colonne_gauche, text=url, anchor="w").pack(fill="x")
        label_statut = ctk.CTkLabel(colonne_gauche, text="⏳ En attente")
        label_statut.pack(anchor="w", pady=5)

        barre_progression = ctk.CTkProgressBar(carte, width=150)
        barre_progression.pack(side="right", padx=10)
        barre_progression.set(0)

        self._cartes[item_id] = {
            "statut": label_statut,
            "progression": barre_progression,
        }

    def _mettre_a_jour_carte(self, item_id, statut, progression):
        carte = self._cartes.get(item_id)
        if not carte:
            return
        carte["statut"].configure(text=statut)
        if "✔️" in statut:
            carte["statut"].configure(text_color="green")
        elif "❌" in statut:
            carte["statut"].configure(text_color="red")
        elif "⬇️" in statut:
            carte["statut"].configure(text_color="cyan")
        else:
            carte["statut"].configure(text_color="gray")
        carte["progression"].set(progression)

    def _schedule_update(self, item_id, statut, progression):
        self.after(0, lambda: self._mettre_a_jour_carte(item_id, statut, progression))

    def _on_ajouter_lien(self):
        url = self._entree_url.get().strip()
        if not url:
            return
        item_id = self._manager.add(url, self._format_selectionne.get())
        self._creer_carte(item_id, url)
        self._entree_url.delete(0, "end")

    def _on_choisir_dossier(self):
        dossier = filedialog.askdirectory()
        if dossier:
            self._manager.set_folder(dossier)

    def _on_choisir_cookies(self):
        chemin = filedialog.askopenfilename(filetypes=[("Cookies", "*.txt")])
        if chemin:
            self._manager.set_cookies(chemin)
        self._refresh_label_cookies()

    def _on_vider_cookies(self):
        self._manager.clear_cookies()
        self._refresh_label_cookies()

    def _on_lancer_telechargement(self):
        self._manager.start()

    def _refresh_label_cookies(self):
        if self._manager.cookies_file:
            self._label_cookies.configure(text="● Cookies: chargés", text_color="green")
        else:
            self._label_cookies.configure(
                text="● Cookies: non chargés", text_color="red"
            )
