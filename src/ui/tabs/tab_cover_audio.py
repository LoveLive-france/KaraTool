import threading
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from core.adaptateurs.composeur_pillow import (
    FACTEUR_HAUTEUR_DEFAUT,
    MARGE_GAUCHE_DEFAUT,
    ComposeurPillow,
)
from core.adaptateurs.ecriveur_mutagen import EcriveurMutagen
from core.cover_manager import (
    HAUTEUR_COVER_DEFAUT,
    LARGEUR_COVER_DEFAUT,
    appliquer_cover,
    generer_cover,
)

_LARGEUR_APERCU = 480


class TabCoverAudio(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._chemin_audio: str | None = None
        self._image_source: Image.Image | None = None
        self._ecriveur = EcriveurMutagen()
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_selection_fichiers()
        self._build_apercu()
        self._build_pied_de_page()

    def _build_selection_fichiers(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(frame, text="Choisir audio", command=self._on_choisir_audio).pack(
            side="left", padx=10, pady=10
        )
        self._label_audio = ctk.CTkLabel(frame, text="Aucun fichier audio sélectionné")
        self._label_audio.pack(side="left", padx=10)

        ctk.CTkButton(frame, text="Choisir image", command=self._on_choisir_image).pack(
            side="left", padx=20
        )
        self._label_image = ctk.CTkLabel(frame, text="Aucune image sélectionnée")
        self._label_image.pack(side="left", padx=10)

    def _build_apercu(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        self._label_image_originale = ctk.CTkLabel(frame, text="Image originale")
        self._label_image_originale.grid(row=0, column=0, padx=10)

        self._label_apercu = ctk.CTkLabel(frame, text="Résultat")
        self._label_apercu.grid(row=0, column=1, padx=10)

    def _build_pied_de_page(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(4, weight=1)

        # Taille de l'image
        ctk.CTkLabel(frame, text="Taille image :").grid(
            row=0, column=0, padx=(10, 4), pady=10
        )
        self._facteur_hauteur = ctk.DoubleVar(value=FACTEUR_HAUTEUR_DEFAUT)
        self._label_facteur = ctk.CTkLabel(
            frame, width=36, text=f"{int(FACTEUR_HAUTEUR_DEFAUT * 100)}%"
        )
        ctk.CTkSlider(
            frame,
            from_=0.3,
            to=1.0,
            variable=self._facteur_hauteur,
            command=self._on_parametre_change,
        ).grid(row=0, column=1, padx=(0, 4), sticky="ew")
        self._label_facteur.grid(row=0, column=2, padx=(0, 16))

        # Marge gauche
        ctk.CTkLabel(frame, text="Marge :").grid(row=0, column=3, padx=(0, 4))
        self._marge_gauche = ctk.DoubleVar(value=MARGE_GAUCHE_DEFAUT)
        self._label_marge = ctk.CTkLabel(
            frame, width=36, text=f"{int(MARGE_GAUCHE_DEFAUT * 100)}%"
        )
        ctk.CTkSlider(
            frame,
            from_=0.0,
            to=0.3,
            variable=self._marge_gauche,
            command=self._on_parametre_change,
        ).grid(row=0, column=4, padx=(0, 4), sticky="ew")
        self._label_marge.grid(row=0, column=5, padx=(0, 16))

        # Boutons + statut
        ctk.CTkButton(
            frame,
            text="Réinitialiser",
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self._on_reinitialiser,
        ).grid(row=0, column=6, padx=(0, 8))
        self._label_statut = ctk.CTkLabel(frame, text="")
        self._label_statut.grid(row=0, column=7, padx=10)
        ctk.CTkButton(frame, text="Appliquer", command=self._on_appliquer).grid(
            row=0, column=8, padx=10, pady=10
        )

    def _composeur_courant(self) -> ComposeurPillow:
        return ComposeurPillow(
            facteur_hauteur=self._facteur_hauteur.get(),
            marge_gauche=self._marge_gauche.get(),
        )

    def _on_choisir_audio(self):
        chemin = filedialog.askopenfilename(
            filetypes=[("Fichiers audio", "*.mp3 *.flac"), ("Tous", "*.*")]
        )
        if chemin:
            self._chemin_audio = chemin
            self._label_audio.configure(text=chemin.split("/")[-1])

    def _on_choisir_image(self):
        chemin = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("Tous", "*.*")]
        )
        if chemin:
            self._label_image.configure(text=chemin.split("/")[-1])
            self._image_source = Image.open(chemin)
            self._rafraichir_apercu()

    def _on_reinitialiser(self):
        self._facteur_hauteur.set(FACTEUR_HAUTEUR_DEFAUT)
        self._marge_gauche.set(MARGE_GAUCHE_DEFAUT)
        self._on_parametre_change()

    def _on_parametre_change(self, _valeur=None):
        self._label_facteur.configure(text=f"{int(self._facteur_hauteur.get() * 100)}%")
        self._label_marge.configure(text=f"{int(self._marge_gauche.get() * 100)}%")
        if self._image_source:
            self._rafraichir_apercu()

    def _rafraichir_apercu(self):
        largeur, hauteur = LARGEUR_COVER_DEFAUT, HAUTEUR_COVER_DEFAUT
        hauteur_apercu = int(_LARGEUR_APERCU * hauteur / largeur)

        largeur_src, hauteur_src = self._image_source.size
        ratio_src = min(_LARGEUR_APERCU / largeur_src, hauteur_apercu / hauteur_src)
        taille_src_affichee = (
            int(largeur_src * ratio_src),
            int(hauteur_src * ratio_src),
        )
        photo_originale = ctk.CTkImage(
            light_image=self._image_source.resize(taille_src_affichee),
            size=taille_src_affichee,
        )
        self._label_image_originale.configure(image=photo_originale, text="")
        self._label_image_originale.image = photo_originale

        image_composee = generer_cover(
            self._image_source, self._composeur_courant(), largeur, hauteur
        )
        image_apercu = image_composee.resize((_LARGEUR_APERCU, hauteur_apercu))
        photo_resultat = ctk.CTkImage(
            light_image=image_apercu, size=(_LARGEUR_APERCU, hauteur_apercu)
        )
        self._label_apercu.configure(image=photo_resultat, text="")
        self._label_apercu.image = photo_resultat

    def _on_appliquer(self):
        if not self._chemin_audio or not self._image_source:
            self._label_statut.configure(
                text="❌ Audio et image requis", text_color="red"
            )
            return
        self._label_statut.configure(text="⏳ En cours…", text_color="gray")
        threading.Thread(target=self._appliquer_cover, daemon=True).start()

    def _appliquer_cover(self):
        try:
            appliquer_cover(
                self._chemin_audio,
                self._image_source,
                self._composeur_courant(),
                self._ecriveur,
            )
            self.after(
                0,
                lambda: self._label_statut.configure(
                    text="✔️ Cover appliquée", text_color="green"
                ),
            )
        except Exception:
            self.after(
                0,
                lambda: self._label_statut.configure(
                    text="❌ Erreur", text_color="red"
                ),
            )
