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
        frame.grid_columnconfigure(1, weight=1)

        self._entree_url = ctk.CTkEntry(frame, placeholder_text="Lien de la vidéo")
        self._entree_url.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self._entree_nom = ctk.CTkEntry(frame, placeholder_text="Nom personnalisé (optionnel)")
        self._entree_nom.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self._format_selectionne = ctk.StringVar(value="Vidéo")
        ctk.CTkOptionMenu(
            frame,
            values=["Vidéo", "Audio"],
            variable=self._format_selectionne,
            command=self._on_format_change,
        ).grid(row=0, column=2, padx=10)

        self._qualite_selectionnee = ctk.StringVar(value="Meilleure")
        self._menu_qualite = ctk.CTkOptionMenu(
            frame,
            values=["Meilleure", "1080p", "720p", "480p"],
            variable=self._qualite_selectionnee,
        )
        self._menu_qualite.grid(row=0, column=3, padx=10)

    def _build_liste(self):
        self._frame_liste = ctk.CTkScrollableFrame(self)
        self._frame_liste.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    def _build_pied_de_page(self):
        # On utilise fg_color="transparent" pour que les sous-frames se fondent dans le fond
        pied = ctk.CTkFrame(self, fg_color="transparent")
        pied.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        # Configuration des colonnes du pied de page pour bien espacer les éléments
        pied.grid_columnconfigure(0, weight=0) # Zone Ajouter
        pied.grid_columnconfigure(1, weight=0) # Zone Dossier
        pied.grid_columnconfigure(2, weight=0) # Zone Cookies
        pied.grid_columnconfigure(3, weight=1) # Espace vide au milieu pour pousser "Télécharger" à droite
        pied.grid_columnconfigure(4, weight=0) # Zone Télécharger

        ctk.CTkButton(pied, text="Ajouter", command=self._on_ajouter_lien).grid(row=0, column=0, padx=10, sticky="n")

        zone_dossier = ctk.CTkFrame(pied, fg_color="transparent")
        zone_dossier.grid(row=0, column=1, padx=10, sticky="n")
        
        ctk.CTkButton(zone_dossier, text="Dossier par défaut", command=self._on_choisir_dossier_defaut).pack()
        
        dossier_actuel = os.path.basename(self._manager.dossier_destination) or self._manager.dossier_destination
        self._label_dossier_defaut = ctk.CTkLabel(zone_dossier, text=f"Actuel : {dossier_actuel}", font=("Arial", 11, "italic"), text_color="gray")
        self._label_dossier_defaut.pack(pady=(2, 0)) # Marge de 2 pixels en haut pour décoller du bouton

        zone_cookies = ctk.CTkFrame(pied, fg_color="transparent")
        zone_cookies.grid(row=0, column=2, padx=10, sticky="n")
        
        ligne_boutons_cookies = ctk.CTkFrame(zone_cookies, fg_color="transparent")
        ligne_boutons_cookies.pack()
        
        ctk.CTkButton(ligne_boutons_cookies, text="Cookies", command=self._on_choisir_cookies, width=90).pack(side="left", padx=(0, 5))
        
        self._btn_vider_cookies = ctk.CTkButton(ligne_boutons_cookies, text="Vider", command=self._on_vider_cookies, width=50, state="disabled")
        self._btn_vider_cookies.pack(side="left")

        self._label_cookies = ctk.CTkLabel(zone_cookies, text="", font=("Arial", 11, "bold"))
        self._label_cookies.pack(pady=(2, 0))

        # --- 4. BOUTON TÉLÉCHARGER TOUT ---
        ctk.CTkButton(pied, text="Télécharger tout", command=self._on_lancer_telechargement).grid(row=0, column=4, padx=10, sticky="n")

    def _creer_carte(self, item_id, url, nom_custom):
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

        ctk.CTkLabel(colonne_gauche, text=url, anchor="w", font=("Arial", 10), text_color="gray").pack(fill="x")

        entree_nom_carte = ctk.CTkEntry(colonne_gauche, placeholder_text="Nom du fichier (optionnel)")
        entree_nom_carte.pack(fill="x", pady=2)
        if nom_custom:
            entree_nom_carte.insert(0, nom_custom)

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
            "entree_nom": entree_nom_carte, 
        }

    def _on_choisir_dossier_defaut(self):
        dossier = filedialog.askdirectory()
        if dossier:
            self._manager.set_folder(dossier)
            nom_dossier = os.path.basename(dossier) if os.path.basename(dossier) else dossier
            self._label_dossier_defaut.configure(text=f"Actuel : {nom_dossier}")

    def _on_choisir_dossier_carte(self, item_id):
        dossier = filedialog.askdirectory()
        if dossier:
            self._cartes[item_id]["dossier_cible"] = dossier
            nom_dossier = os.path.basename(dossier) if os.path.basename(dossier) else dossier
            self._cartes[item_id]["label_dossier"].configure(
                text=f"Dossier : .../{nom_dossier}", text_color="white"
            )

    def _supprimer_carte(self, item_id):
        donnees_carte = self._cartes.get(item_id)
        if donnees_carte:
            donnees_carte["widget"].destroy()
            del self._cartes[item_id]
            self._manager.remove(item_id) # On supprime du gestionnaire comme vu précédemment

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
        nom_custom = self._entree_nom.get().strip()
        if not url:
            return
            
        item_id = self._manager.add(
            url, 
            self._format_selectionne.get(), 
            self._qualite_selectionnee.get(),
            nom_custom if nom_custom else None
        )
        self._creer_carte(item_id, url, nom_custom)
        
        self._entree_url.delete(0, "end")
        self._entree_nom.delete(0, "end")

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
            nom_final = infos["entree_nom"].get().strip()
            self._manager.set_name_for_item(item_id, nom_final if nom_final else None)

            if infos["dossier_cible"]:
                try:
                    self._manager.set_folder_for_item(item_id, infos["dossier_cible"])
                except AttributeError:
                    pass

        self._manager.start()

    def _refresh_label_cookies(self):
        if self._manager.cookies_file:
            self._label_cookies.configure(text="● Chargés", text_color="green")
            self._btn_vider_cookies.configure(state="normal") # Active le bouton "Vider"
        else:
            self._label_cookies.configure(text="○ Non chargés", text_color="gray")
            self._btn_vider_cookies.configure(state="disabled") # Désactive le bouton "Vider"