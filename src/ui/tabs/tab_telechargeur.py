import os
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
        self._build_barre_saisie()
        self._build_liste()
        self._build_pied_de_page()

    def _build_barre_saisie(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)

        self._entree_url = ctk.CTkEntry(frame, placeholder_text="Lien")
        self._entree_url.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self._format_selectionne = ctk.StringVar(value="Vidéo")
        ctk.CTkOptionMenu(
            frame,
            values=["Vidéo", "Audio"],
            variable=self._format_selectionne,
            command=self._on_format_change,
        ).grid(row=0, column=1, padx=10)

        self._qualite_selectionnee = ctk.StringVar(value="Meilleure")
        self._menu_qualite = ctk.CTkOptionMenu(
            frame,
            values=["Meilleure", "1080p", "720p", "480p"],
            variable=self._qualite_selectionnee,
        )
        self._menu_qualite.grid(row=0, column=2, padx=10)

    def _build_liste(self):
        self._frame_liste = ctk.CTkScrollableFrame(self)
        self._frame_liste.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    def _build_pied_de_page(self):
        pied = ctk.CTkFrame(self)
        pied.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(pied, text="Ajouter", command=self._on_ajouter_lien).pack(
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
        self._label_cookies.pack(side="left", padx=10)

    def _creer_carte(self, item_id, url):
        carte = ctk.CTkFrame(self._frame_liste, corner_radius=12)
        carte.pack(fill="x", padx=10, pady=8)

        ctk.CTkButton(
            carte,
            text="Retirer",
            width=70,
            fg_color="#A83232",
            hover_color="#7A2222",
            command=lambda: self._supprimer_carte(item_id),
        ).pack(side="left", padx=10, pady=10)

        btn_dossier = ctk.CTkButton(
            carte,
            text="📁 Dossier",
            width=100,
            command=lambda: self._on_choisir_dossier_carte(item_id),
        )
        btn_dossier.pack(side="left", padx=5, pady=10)

        colonne_gauche = ctk.CTkFrame(carte, fg_color="transparent")
        colonne_gauche.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(colonne_gauche, text=url, anchor="w").pack(fill="x")

        label_dossier = ctk.CTkLabel(
            colonne_gauche,
            text="Dossier : Par défaut",
            font=("Arial", 11, "italic"),
            text_color="gray",
        )
        label_dossier.pack(anchor="w")

        label_statut = ctk.CTkLabel(colonne_gauche, text="⏳ En attente")
        label_statut.pack(anchor="w", pady=2)

        barre_progression = ctk.CTkProgressBar(carte, width=150)
        barre_progression.pack(side="right", padx=10)
        barre_progression.set(0)

        self._cartes[item_id] = {
            "widget": carte,
            "statut": label_statut,
            "progression": barre_progression,
            "label_dossier": label_dossier,
            "btn_dossier": btn_dossier,
            "dossier_cible": None,
        }

    def _on_choisir_dossier_carte(self, item_id):
        dossier = filedialog.askdirectory()
        if dossier:
            self._cartes[item_id]["dossier_cible"] = dossier

            nom_dossier = (
                os.path.basename(dossier) if os.path.basename(dossier) else dossier
            )
            self._cartes[item_id]["label_dossier"].configure(
                text=f"Dossier : .../{nom_dossier}", text_color="white"
            )

    def _supprimer_carte(self, item_id):
        donnees_carte = self._cartes.get(item_id)
        if donnees_carte:
            donnees_carte["widget"].destroy()
            del self._cartes[item_id]

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

    def _on_format_change(self, format_selectionne):
        etat = "normal" if format_selectionne == "Vidéo" else "disabled"
        self._menu_qualite.configure(state=etat)

    def _on_ajouter_lien(self):
        url = self._entree_url.get().strip()
        if not url:
            return
        item_id = self._manager.add(
            url, self._format_selectionne.get(), self._qualite_selectionnee.get()
        )
        self._creer_carte(item_id, url)
        self._entree_url.delete(0, "end")

    def _on_choisir_cookies(self):
        chemin = filedialog.askopenfilename(filetypes=[("Cookies", "*.txt")])
        if chemin:
            self._manager.set_cookies(chemin)
        self._refresh_label_cookies()

    def _on_vider_cookies(self):
        self._manager.clear_cookies()
        self._refresh_label_cookies()

    def _on_lancer_telechargement(self):
        for item_id, infos in self._cartes.items():
            if infos["dossier_cible"]:
                try:
                    self._manager.set_folder_for_item(item_id, infos["dossier_cible"])
                except AttributeError:
                    print(
                        f"Erreur : Ton DownloadManager n'a pas de méthode pour attribuer un dossier à l'item {item_id}"
                    )

        self._manager.start()

    def _refresh_label_cookies(self):
        if self._manager.cookies_file:
            self._label_cookies.configure(text="● Cookies: chargés", text_color="green")
        else:
            self._label_cookies.configure(
                text="",
            )
