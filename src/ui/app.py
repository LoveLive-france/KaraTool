import customtkinter as ctk
from ui.tabs.tab_telechargeur import TabTelechargeur
from ui.tabs.tab_texte_japonais import TabTexteJaponais

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LLFR Tools")
        self.geometry("1000x650")
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        onglets = ctk.CTkTabview(self)
        onglets.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        TabTelechargeur(onglets.add("Téléchargeur")).pack(fill="both", expand=True)
        TabTexteJaponais(onglets.add("Formattage Kara")).pack(fill="both", expand=True)
