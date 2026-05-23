import customtkinter as ctk
from tkinter import filedialog
from core.ass_exporter import (
    exporter_ass,
    extraire_styles_depuis_ass,
    fusionner_styles,
    lire_styles_disponibles,
    reinitialiser_styles,
    sauvegarder_styles,
)
from core.formattage_kara.romaniseur import romaniser_texte


class TabTexteJaponais(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._styles_disponibles = lire_styles_disponibles()
        self._styles_selectionnes = []
        self._cadre_deroulant: ctk.CTkFrame | None = None
        self._cases: dict[str, ctk.BooleanVar] = {}
        self._deroulant_ouvert = False
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            self,
            text="Charger les styles d'un .ass",
            command=self._charger_styles_depuis_ass,
        ).grid(row=0, column=0, pady=(10, 5), padx=(10, 5), sticky="ew")

        self._bouton_styles = ctk.CTkButton(
            self,
            text=self._label_styles(),
            command=self._ouvrir_selecteur_styles,
        )
        self._bouton_styles.grid(
            row=0, column=1, pady=(10, 5), padx=(5, 10), sticky="ew"
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
            row=2, column=0, pady=(5, 0), padx=10, sticky="w"
        )

        self._entree_nom_fichier = ctk.CTkEntry(self, placeholder_text="Nom du fichier")
        self._entree_nom_fichier.grid(
            row=2, column=1, sticky="ew", padx=(5, 10), pady=(5, 0)
        )

        ctk.CTkButton(self, text="Romaniser", command=self._on_romaniser).grid(
            row=3, column=0, pady=(5, 10), padx=(10, 5), sticky="ew"
        )
        ctk.CTkButton(
            self, text="Télécharger .ass", command=self._on_telecharger_ass
        ).grid(row=3, column=1, pady=(5, 10), padx=(5, 10), sticky="ew")

    def _label_styles(self) -> str:
        n = len(self._styles_selectionnes)
        total = len(self._styles_disponibles)
        return f"Styles à ajouter au .ass généré ({n}/{total})"

    def _creer_cadre_deroulant(self) -> ctk.CTkFrame:
        cadre = ctk.CTkFrame(self, corner_radius=8)
        cadre.grid_columnconfigure((0, 1), weight=1)

        zone_scroll = ctk.CTkScrollableFrame(cadre, height=250)
        zone_scroll.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4)
        )

        self._cases = {}
        for i, style in enumerate(self._styles_disponibles):
            var = ctk.BooleanVar(value=style["nom"] in self._styles_selectionnes)
            ctk.CTkCheckBox(zone_scroll, text=style["nom"], variable=var).grid(
                row=i, column=0, sticky="w", padx=4, pady=2
            )
            self._cases[style["nom"]] = var

        ctk.CTkButton(cadre, text="Valider", command=self._fermer_deroulant).grid(
            row=1, column=0, padx=(12, 4), pady=(4, 10), sticky="ew"
        )
        ctk.CTkButton(
            cadre,
            text="Réinitialiser",
            command=self._reinitialiser_styles,
            fg_color="#8B1A1A",
            hover_color="#6B1414",
        ).grid(row=1, column=1, padx=(4, 12), pady=(4, 10), sticky="ew")
        return cadre

    def _ouvrir_selecteur_styles(self):
        if self._deroulant_ouvert:
            self._fermer_deroulant()
            return
        self._cadre_deroulant = self._creer_cadre_deroulant()
        self._bouton_styles.update_idletasks()
        y = self._bouton_styles.winfo_y() + self._bouton_styles.winfo_height()
        self._cadre_deroulant.place(relx=1.0, y=y, anchor="ne")
        self._cadre_deroulant.lift()
        self._deroulant_ouvert = True

    def _fermer_deroulant(self):
        self._styles_selectionnes = [
            nom for nom, var in self._cases.items() if var.get()
        ]
        self._bouton_styles.configure(text=self._label_styles())
        self._cadre_deroulant.destroy()
        self._cadre_deroulant = None
        self._deroulant_ouvert = False

    def _reinitialiser_styles(self):
        reinitialiser_styles()
        self._styles_disponibles = lire_styles_disponibles()
        self._styles_selectionnes = []
        self._bouton_styles.configure(text=self._label_styles())
        if self._deroulant_ouvert:
            self._fermer_deroulant()
            self._ouvrir_selecteur_styles()

    def _charger_styles_depuis_ass(self):
        chemin = filedialog.askopenfilename(
            filetypes=[("SubStation Alpha", "*.ass")],
        )
        if not chemin:
            return
        nouveaux = extraire_styles_depuis_ass(chemin)
        noms_avant = {s["nom"] for s in self._styles_disponibles}
        fusionnes = fusionner_styles(self._styles_disponibles, nouveaux)
        sauvegarder_styles(fusionnes)
        self._styles_disponibles = fusionnes
        self._styles_selectionnes.extend(
            s["nom"] for s in fusionnes if s["nom"] not in noms_avant
        )
        if self._deroulant_ouvert:
            self._fermer_deroulant()
            self._ouvrir_selecteur_styles()

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
            exporter_ass(
                chemin_destination,
                romaji.splitlines(),
                titre=nom_fichier,
                styles_a_inclure=self._styles_selectionnes,
            )
