import os
import sys
import tempfile
import threading
from pathlib import Path

import customtkinter as ctk

from core.auto_updater import lancer_remplacement, telecharger_exe


class DialogMiseAJour(ctk.CTkToplevel):
    def __init__(self, parent, info_version: dict):
        super().__init__(parent)
        self._info_version = info_version
        self._chemin_exe_actuel = sys.executable
        self.title("Mise à jour disponible")
        self.geometry("400x160")
        self.resizable(False, False)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        conteneur = ctk.CTkFrame(self)
        conteneur.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        conteneur.grid_columnconfigure(0, weight=1)

        version = self._info_version["version"]
        ctk.CTkLabel(conteneur, text=f"Nouvelle version disponible : {version}").grid(
            row=0, column=0, columnspan=2, pady=(0, 12)
        )

        self._barre_progression = ctk.CTkProgressBar(conteneur)
        self._barre_progression.set(0)
        self._barre_progression.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12)
        )

        self._bouton_mettre_a_jour = ctk.CTkButton(
            conteneur,
            text="Mettre à jour et redémarrer",
            command=self._on_mettre_a_jour,
        )
        self._bouton_mettre_a_jour.grid(row=2, column=0, padx=(0, 8))

        ctk.CTkButton(
            conteneur, text="Plus tard", fg_color="gray", command=self.destroy
        ).grid(row=2, column=1)

    def _on_mettre_a_jour(self):
        self._bouton_mettre_a_jour.configure(state="disabled")
        threading.Thread(target=self._telecharger_et_installer, daemon=True).start()

    def _telecharger_et_installer(self):
        chemin_nouveau = str(Path(tempfile.gettempdir()) / "KaraTool_update.exe")
        try:
            telecharger_exe(
                self._info_version["url_download"],
                chemin_nouveau,
                self._on_progression,
            )
        except Exception:
            self.after(0, self._on_erreur_telechargement)
            return
        lancer_remplacement(chemin_nouveau, self._chemin_exe_actuel)
        # @devnote : sys.exit() depuis un thread daemon lève SystemExit sur ce thread
        # uniquement, Tkinter continue. os._exit() termine le processus entier.
        os._exit(0)

    def _on_progression(self, octets_recus: int, taille_totale: int):
        if taille_totale > 0:
            progression = octets_recus / taille_totale
            self.after(0, lambda: self._barre_progression.set(progression))

    def _on_erreur_telechargement(self):
        self._bouton_mettre_a_jour.configure(state="normal", text="Réessayer")
