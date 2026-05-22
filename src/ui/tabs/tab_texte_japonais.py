import customtkinter as ctk
from tkinter import filedialog
from core.text_exporter import exporter_texte


class TabTexteJaponais(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    # ---------- BUILD ----------

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._entree_nom_fichier = ctk.CTkEntry(self, placeholder_text="Nom du fichier")
        self._entree_nom_fichier.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        self._zone_texte_japonais = ctk.CTkTextbox(self, font=("Arial", 16))
        self._zone_texte_japonais.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        ctk.CTkButton(self, text="Télécharger .txt", command=self._on_telecharger_texte).grid(
            row=2, column=0, pady=(5, 10)
        )

    # ---------- ACTIONS ----------

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
