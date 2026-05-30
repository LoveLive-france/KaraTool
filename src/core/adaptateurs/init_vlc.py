# init_vlc.py
import os
import sys
import winreg
from tkinter import messagebox

# On exécute la détection directement au chargement du fichier
chemins_registre = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VideoLAN\VLC", winreg.KEY_READ | winreg.KEY_WOW64_64KEY),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VideoLAN\VLC", winreg.KEY_READ | winreg.KEY_WOW64_32KEY),
]

vlc_trouve = False
for ruche, sous_cle, acces in chemins_registre:
    try:
        cle = winreg.OpenKey(ruche, sous_cle, 0, acces)
        dossier_vlc, _ = winreg.QueryValueEx(cle, "InstallDir")
        winreg.CloseKey(cle)
        if os.path.exists(dossier_vlc):
            os.environ["PYTHON_VLC_MODULE_PATH"] = dossier_vlc
            vlc_trouve = True
            break
    except FileNotFoundError:
        continue

if not vlc_trouve:
    messagebox.showerror("VLC Introuvable", "VLC n'a pas été détecté.")
    sys.exit(1)