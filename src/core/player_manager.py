from pathlib import Path
import os
import sys
import winreg
from tkinter import messagebox

def detecter_et_configurer_vlc():
    # Interroge Windows pour obtenir le chemin d'installation de VLC.
    # Récupère le chemin ABSOLU complet, ce qui gère automatiquement les cas
    # où VLC est installé sur un autre disque (D:, E:, etc.).
    chemins_registre = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VideoLAN\VLC", winreg.KEY_READ | winreg.KEY_WOW64_64KEY),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VideoLAN\VLC", winreg.KEY_READ | winreg.KEY_WOW64_32KEY),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\VideoLAN\VLC", winreg.KEY_READ)
    ]
    
    for ruche, sous_cle, acces in chemins_registre:
        try:
            cle = winreg.OpenKey(ruche, sous_cle, 0, acces)
            dossier_vlc, _ = winreg.QueryValueEx(cle, "InstallDir")
            winreg.CloseKey(cle)
            
            # Si le dossier existe (Peu importe le disque : C:\..., D:\..., etc.)
            if os.path.exists(dossier_vlc):
                # On dit à python-vlc de regarder STRICTEMENT dans ce dossier
                os.environ["PYTHON_VLC_MODULE_PATH"] = dossier_vlc
                return True
        except FileNotFoundError:
            continue
    return False

# --- ÉTAPE CRUCIALE AVANT TOUT IMPORT DE TON CODE ---
if not detecter_et_configurer_vlc():
    messagebox.showerror(
        "VLC Introuvable",
        "L'application n'a pas pu détecter le lecteur VLC sur votre ordinateur.\n\n"
        "Veuillez vérifier que VLC est bien installé sur votre système."
    )
    sys.exit(1)

import vlc

class PlayerManager:
    def __init__(self):
        self.instance = vlc.Instance(
            "--no-video-title-show", 
            "--input-fast-seek",
            "--clock-jitter=0" 
        )
        self.player = self.instance.media_player_new()

    def load_media(self, image_path, audio_path=None, subtitle_path=None, duration=None):
        self.player.stop()

        # 1. Image principale (chemin absolu standard)
        abs_image_path = str(Path(image_path).absolute())
        options = []
        
        # 2. Configuration de l'audio esclave (Lui accepte l'URI sans broncher)
        if audio_path:
            audio_uri = Path(audio_path).absolute().as_uri()
            options.append(f":input-slave={audio_uri}")
            
            # On garde le fix des 60 FPS pour la fluidité des effets \kf
            options.append(":image-fps=30")
            
            if duration:
                options.append(f":image-duration={int(duration)}")
            else:
                options.append(":image-duration=-1")
        
        # 3. Correction ici : On repasse en chemin absolu CLASSIQUE pour Windows
        if subtitle_path and os.path.exists(subtitle_path):
            abs_sub_path = str(Path(subtitle_path).absolute())
            options.append(f":sub-file={abs_sub_path}")
            
        # 4. Chargement du média
        media = self.instance.media_new(abs_image_path, *options)
        self.player.set_media(media)

    def attach_window(self, handle):
        if os.name == "nt":
            self.player.set_hwnd(handle)
        else:
            self.player.set_xwindow(handle)

    def play(self): self.player.play()
    def pause(self): self.player.pause()
    def stop(self): self.player.stop()
    def set_volume(self, value): self.player.audio_set_volume(int(value))