# init_vlc.py
import os
import sys
import winreg
from tkinter import messagebox

# On exécute la détection directement au chargement du fichier
chemins_registre = [
    (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\VideoLAN\VLC",
        winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
    ),
    (
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\VideoLAN\VLC",
        winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
    ),
]

vlc_trouve = False
for ruche, sous_cle, acces in chemins_registre:
    try:
        cle = winreg.OpenKey(ruche, sous_cle, 0, acces)
        dossier_vlc, _ = winreg.QueryValueEx(cle, "InstallDir")
        winreg.CloseKey(cle)

        if os.path.exists(dossier_vlc):
            # ON COUPE COURT AUX RECHERCHES DE WINDOWS :
            # On pointe directement sur le fichier DLL du bon disque (D:, E:, etc.)
            chemin_direct_dll = os.path.join(dossier_vlc, "libvlc.dll")

            if os.path.exists(chemin_direct_dll):
                os.environ["PYTHON_VLC_MODULE_PATH"] = dossier_vlc
                os.environ["PYTHON_VLC_LIB_PATH"] = (
                    chemin_direct_dll  # <-- Le verrou est ici
                )
                vlc_trouve = True
                break
    except FileNotFoundError:
        continue

if not vlc_trouve:
    messagebox.showerror(
        "VLC Introuvable", "Impossible de localiser proprement VLC sur votre système."
    )
    sys.exit(1)

# Pour satisfaire Ruff (F401) dans main.py
VLC_READY = True
