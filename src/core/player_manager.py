import os
from pathlib import Path
import sys
from tkinter import messagebox
import winreg
import vlc


class PlayerManager:
    vlc_trouve = None

    def __init__(self):
        self.instance = None
        self.player = None
        self._pending_handle = None

    def _initialiser_vlc_si_necessaire(self):
        if PlayerManager.vlc_trouve is True:
            return

        if PlayerManager.vlc_trouve is False:
            self._declencher_erreur_vlc()

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

        vlc_detecte = False
        if os.name == "nt":
            for ruche, sous_cle, acces in chemins_registre:
                try:
                    cle = winreg.OpenKey(ruche, sous_cle, 0, acces)
                    dossier_vlc, _ = winreg.QueryValueEx(cle, "InstallDir")
                    winreg.CloseKey(cle)

                    if os.path.exists(dossier_vlc):
                        chemin_direct_dll = os.path.join(dossier_vlc, "libvlc.dll")
                        if os.path.exists(chemin_direct_dll):
                            os.environ["PYTHON_VLC_MODULE_PATH"] = dossier_vlc
                            os.environ["PYTHON_VLC_LIB_PATH"] = chemin_direct_dll
                            vlc_detecte = True
                            break
                except FileNotFoundError:
                    continue
        else:
            vlc_detecte = True

        if not vlc_detecte:
            PlayerManager.vlc_trouve = False
            self._declencher_erreur_vlc()

        PlayerManager.vlc_trouve = True

        self.instance = vlc.Instance(
            "--no-video-title-show", "--input-fast-seek", "--clock-jitter=0"
        )
        self.player = self.instance.media_player_new()

        if self._pending_handle:
            self._appliquer_attach_window(self._pending_handle)

    def _declencher_erreur_vlc(self):
        """Affiche le message d'erreur et ferme l'application."""
        messagebox.showerror(
            "VLC Introuvable",
            "Impossible de localiser proprement VLC sur votre système.\nL'application va se fermer.",
        )
        sys.exit(1)

    def load_media(
        self, image_path, audio_path=None, subtitle_path=None, duration=None
    ):
        self._initialiser_vlc_si_necessaire()

        self.player.stop()

        abs_image_path = str(Path(image_path).absolute())
        options = []

        if audio_path:
            audio_uri = Path(audio_path).absolute().as_uri()
            options.append(f":input-slave={audio_uri}")
            options.append(":image-fps=30")

            if duration:
                options.append(f":image-duration={int(duration)}")
            else:
                options.append(":image-duration=-1")

        if subtitle_path and os.path.exists(subtitle_path):
            abs_sub_path = str(Path(subtitle_path).absolute())
            options.append(f":sub-file={abs_sub_path}")

        media = self.instance.media_new(abs_image_path, *options)
        self.player.set_media(media)

    def attach_window(self, handle):
        if not self.player:
            self._pending_handle = handle
            return
        self._appliquer_attach_window(handle)

    def _appliquer_attach_window(self, handle):
        if os.name == "nt":
            self.player.set_hwnd(handle)
        else:
            self.player.set_xwindow(handle)

    def play(self):
        self._initialiser_vlc_si_necessaire()
        self.player.play()

    def pause(self):
        if self.player:
            self.player.pause()

    def stop(self):
        if self.player:
            self.player.stop()

    def set_volume(self, value):
        if self.player:
            self.player.audio_set_volume(int(value))
