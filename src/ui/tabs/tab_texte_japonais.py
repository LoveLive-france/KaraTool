import customtkinter as ctk
from tkinter import filedialog
from core.text_exporter import exporter_texte
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
        self._entree_nom_fichier.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        self._zone_texte_japonais = ctk.CTkTextbox(self, font=("Arial", 16))
        self._zone_texte_japonais.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)

        self._zone_romaji = ctk.CTkTextbox(self, font=("Arial", 16), state="disabled")
        self._zone_romaji.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)

        ctk.CTkButton(self, text="Romaniser", command=self._on_romaniser).grid(
            row=2, column=0, pady=(5, 10), padx=(10, 5), sticky="ew"
        )
        ctk.CTkButton(self, text="Télécharger .txt", command=self._on_telecharger_texte).grid(
            row=2, column=1, pady=(5, 10), padx=(5, 10), sticky="ew"
        )

    def _on_romaniser(self):
        contenu = self._zone_texte_japonais.get("1.0", "end-1c")
        romaji = romaniser_texte(contenu)
        self._zone_romaji.configure(state="normal")
        self._zone_romaji.delete("1.0", "end")
        self._zone_romaji.insert("1.0", romaji)
        self._zone_romaji.configure(state="disabled")

    def _on_telecharger_texte(self):
        contenu = self._zone_texte_japonais.get("1.0", "end-1c")
        nom_fichier = self._entree_nom_fichier.get().strip() or "texte"
        chemin_destination = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt")],
            initialfile=nom_fichier,
        )
        if chemin_destination:
            exporter_texte(chemin_destination, contenu)
