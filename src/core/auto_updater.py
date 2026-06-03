import os
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import requests

_URL_DERNIERE_RELEASE = (
    "https://api.github.com/repos/LoveLive-france/KaraTool/releases/latest"
)


def verifier_nouvelle_version(version_actuelle: str) -> dict | None:
    try:
        reponse = requests.get(_URL_DERNIERE_RELEASE, timeout=5)
        reponse.raise_for_status()
        donnees = reponse.json()
        version_disponible = donnees["tag_name"]
        if version_disponible == version_actuelle:
            return None
        url_download = _extraire_url_download(donnees["assets"], version_disponible)
        if url_download is None:
            return None
        return {"version": version_disponible, "url_download": url_download}
    except Exception:
        return None


def telecharger_exe(
    url: str,
    chemin_destination: str,
    callback_progression: Callable[[int, int], None],
) -> None:
    reponse = requests.get(url, stream=True, timeout=30)
    reponse.raise_for_status()
    taille_totale = int(reponse.headers.get("content-length", 0))
    octets_recus = 0
    with open(chemin_destination, "wb") as fichier:
        for chunk in reponse.iter_content(chunk_size=8192):
            fichier.write(chunk)
            octets_recus += len(chunk)
            callback_progression(octets_recus, taille_totale)


def lancer_remplacement(chemin_nouveau: str, chemin_actuel: str) -> None:
    # @devnote : l'exe PyInstaller est verrouillé pendant son exécution sous Windows,
    # impossible de le remplacer directement. Le bat attend la mort du processus via son PID
    # plutôt qu'un timeout fixe — PyInstaller peut mettre plusieurs secondes à nettoyer _MEI.
    pid = os.getpid()
    contenu_bat = (
        "@echo off\n"
        f":ATTENTE\n"
        f'tasklist /FI "PID eq {pid}" 2>NUL | find /I "{pid}" >NUL\n'
        f"if not errorlevel 1 (\n"
        f"    timeout /t 1 /nobreak > nul\n"
        f"    goto ATTENTE\n"
        f")\n"
        "timeout /t 2 /nobreak > nul\n"
        f'move /y "{chemin_nouveau}" "{chemin_actuel}"\n'
        f'start "" "{chemin_actuel}"\n'
        'del "%~f0"\n'
    )
    chemin_bat = Path(tempfile.gettempdir()) / "karatool_update.bat"
    chemin_bat.write_text(contenu_bat, encoding="utf-8")
    # @devnote : CREATE_NO_WINDOW requis pour apps sans console (PyInstaller console=False) —
    # DETACHED_PROCESS est ignoré dans ce contexte et empêche cmd.exe de démarrer correctement.
    subprocess.Popen(
        ["cmd", "/c", str(chemin_bat)],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _extraire_url_download(assets: list, version: str) -> str | None:
    nom_attendu = f"KaraTool_{version}.exe"
    for asset in assets:
        if asset["name"] == nom_attendu:
            return asset["browser_download_url"]
    return None
