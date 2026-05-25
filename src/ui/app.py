import threading

import customtkinter as ctk

from ui.tabs.tab_telechargeur import TabTelechargeur
from ui.tabs.tab_texte_japonais import TabTexteJaponais
from ui.tabs.tab_encodage import TabEncodeur
from ui.tabs.tab_cover_audio import TabCoverAudio
from ui.tabs.tab_lecteur import TabLecteur

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        try:
            from version import __version__

            self._version = __version__
        except ImportError:
            self._version = None
        self.title(f"LLFR Tools {self._version}" if self._version else "LLFR Tools")
        self.geometry("1000x650")
        self._build_ui()
        if self._version:
            threading.Thread(target=self._verifier_mise_a_jour, daemon=True).start()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        onglets = ctk.CTkTabview(self)
        onglets.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        TabTelechargeur(onglets.add("Téléchargeur")).pack(fill="both", expand=True)
        TabTexteJaponais(onglets.add("Formattage Kara")).pack(fill="both", expand=True)
        TabEncodeur(onglets.add("Réencodage Vidéo")).pack(fill="both", expand=True)
        TabCoverAudio(onglets.add("Cover Audio")).pack(fill="both", expand=True)
        TabLecteur(onglets.add("Lecteur Vidéo")).pack(fill="both", expand=True)

    def _verifier_mise_a_jour(self):
        from core.auto_updater import verifier_nouvelle_version
        from ui.dialog_mise_a_jour import DialogMiseAJour

        info = verifier_nouvelle_version(self._version)
        if info:
            self.after(0, lambda: DialogMiseAJour(self, info))
