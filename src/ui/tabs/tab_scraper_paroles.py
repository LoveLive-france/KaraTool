import customtkinter as ctk

from core.scraper_paroles import extraire_paroles_japonaises
from core.scraper_paroles_fandom import ErreurScrapingParoles


class TabScraperParoles(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame_saisie = ctk.CTkFrame(self, fg_color="transparent")
        frame_saisie.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        frame_saisie.grid_columnconfigure(0, weight=1)

        self._entree_url = ctk.CTkEntry(
            frame_saisie,
            placeholder_text="URL wiki Love Live ou uta-net.com",
        )
        self._entree_url.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self._bouton_recuperer = ctk.CTkButton(
            frame_saisie, text="Récupérer les paroles", command=self._on_recuperer
        )
        self._bouton_recuperer.grid(row=0, column=1)

        self._label_statut = ctk.CTkLabel(self, text="", anchor="w")
        self._label_statut.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        self._zone_apercu = ctk.CTkTextbox(self, font=("Arial", 16))
        self._zone_apercu.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _on_recuperer(self):
        url_page = self._entree_url.get().strip()
        if not url_page:
            return

        self._bouton_recuperer.configure(state="disabled")
        self._label_statut.configure(
            text="⏳ Récupération en cours...", text_color="gray"
        )
        self._zone_apercu.delete("1.0", "end")
        self.update_idletasks()

        try:
            paroles_japonaises = extraire_paroles_japonaises(url_page)
        except (ErreurScrapingParoles, ValueError) as erreur:
            self._label_statut.configure(text=f"❌ {erreur}", text_color="red")
            self._bouton_recuperer.configure(state="normal")
            return

        self._zone_apercu.insert("1.0", paroles_japonaises)
        self._label_statut.configure(text="✔️ Paroles récupérées", text_color="green")
        self._bouton_recuperer.configure(state="normal")
        self._envoyer_vers_formattage_kara(paroles_japonaises)

    def _envoyer_vers_formattage_kara(self, paroles_japonaises: str):
        app = self.winfo_toplevel()
        onglet_formattage = app.obtenir_ou_creer_frame("Formattage Kara")
        onglet_formattage.definir_texte_japonais(paroles_japonaises)
        app._select_frame("Formattage Kara")
