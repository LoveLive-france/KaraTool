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

        self._sidebar_visible = True
        self.frames = {}

        self._build_ui()

        if self._version:
            threading.Thread(target=self._verifier_mise_a_jour, daemon=True).start()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.label_titre = ctk.CTkLabel(
            self.sidebar_frame, text="Menu", font=("Arial", 20, "bold")
        )
        self.label_titre.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.main_container = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.header_frame = ctk.CTkFrame(
            self.main_container, height=50, corner_radius=0, fg_color="transparent"
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")

        self.btn_burger = ctk.CTkButton(
            self.header_frame,
            text="☰",
            width=40,
            height=40,
            font=("Arial", 24),
            fg_color="transparent",
            hover_color="#333333",
            command=self._toggle_sidebar,
        )
        self.btn_burger.pack(side="left", padx=10, pady=10)

        self.label_page = ctk.CTkLabel(
            self.header_frame, text="", font=("Arial", 18, "bold")
        )
        self.label_page.pack(side="left", padx=10, pady=10)

        self.content_frame = ctk.CTkFrame(
            self.main_container, corner_radius=0, fg_color="transparent"
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.frames["Téléchargeur"] = TabTelechargeur(self.content_frame)
        self.frames["Formattage Kara"] = TabTexteJaponais(self.content_frame)
        self.frames["Réencodage"] = TabEncodeur(self.content_frame)
        self.frames["Cover Audio"] = TabCoverAudio(self.content_frame)
        self.frames["Lecteur"] = TabLecteur(self.content_frame)

        boutons_menu = [
            "Téléchargeur",
            "Formattage Kara",
            "Réencodage",
            "Cover Audio",
            "Lecteur",
        ]
        for i, nom in enumerate(boutons_menu, start=1):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=nom,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                command=lambda n=nom: self._select_frame(n),
            )
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

        self._select_frame("Téléchargeur")

    def _select_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()

        self.frames[name].pack(fill="both", expand=True)
        self.label_page.configure(text=name)

    def _toggle_sidebar(self):
        if self._sidebar_visible:
            self.sidebar_frame.grid_forget()
            self._sidebar_visible = False
        else:
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
            self._sidebar_visible = True

    def _verifier_mise_a_jour(self):
        from core.auto_updater import verifier_nouvelle_version
        from ui.dialog_mise_a_jour import DialogMiseAJour

        info = verifier_nouvelle_version(self._version)
        if info:
            self.after(0, lambda: DialogMiseAJour(self, info))
