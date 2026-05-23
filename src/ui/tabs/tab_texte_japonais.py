import customtkinter as ctk
from tkinter import filedialog
from core.ass_exporter import exporter_ass
from core.formattage_kara.romaniseur import romaniser_texte


class TabTexteJaponais(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._entree_nom_fichier = ctk.CTkEntry(self, placeholder_text="Nom du fichier")
        self._entree_nom_fichier.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5)
        )

        self._zone_texte_japonais = ctk.CTkTextbox(self, font=("Arial", 16))
        self._zone_texte_japonais.grid(
            row=1, column=0, sticky="nsew", padx=(10, 5), pady=5
        )

        self._zone_romaji = ctk.CTkTextbox(self, font=("Arial", 16))
        self._zone_romaji.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)

        self._toggle_conserver_casse = ctk.CTkSwitch(
            self, text="Conserver la casse des lignes latines"
        )
        self._toggle_conserver_casse.grid(
            row=2, column=0, columnspan=2, pady=(5, 0), padx=10, sticky="w"
        )

        ctk.CTkButton(self, text="Romaniser", command=self._on_romaniser).grid(
            row=3, column=0, pady=(5, 10), padx=(10, 5), sticky="ew"
        )
        ctk.CTkButton(
            self, text="Télécharger .ass", command=self._on_telecharger_ass
        ).grid(row=3, column=1, pady=(5, 10), padx=(5, 10), sticky="ew")

    def _on_romaniser(self):
        contenu = self._zone_texte_japonais.get("1.0", "end-1c")
        romaji = romaniser_texte(
            contenu, conserver_casse_latine=self._toggle_conserver_casse.get()
        )
        self._zone_romaji.delete("1.0", "end")
        self._zone_romaji.insert("1.0", romaji)

    def _on_telecharger_ass(self):
        romaji = self._zone_romaji.get("1.0", "end-1c")
        nom_fichier = self._entree_nom_fichier.get().strip() or "subtitles"
        chemin_destination = filedialog.asksaveasfilename(
            defaultextension=".ass",
            filetypes=[("SubStation Alpha", "*.ass")],
            initialfile=nom_fichier,
        )
        if chemin_destination:
            exporter_ass(chemin_destination, romaji.splitlines(), titre=nom_fichier)
