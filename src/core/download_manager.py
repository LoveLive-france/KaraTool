import os
import sys
import threading
from yt_dlp import YoutubeDL


def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.getcwd()


def build_ydl_opts(
    url, format_media, dossier_destination, cookies_file=None, rappel_progression=None
):
    options_telechargement = {
        "outtmpl": os.path.join(dossier_destination, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    if rappel_progression:
        options_telechargement["progress_hooks"] = [rappel_progression]

    if cookies_file:
        options_telechargement["cookiefile"] = cookies_file

    if format_media == "Vidéo":
        options_telechargement.update(
            {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "ffmpeg_location": get_ffmpeg_path(),
            }
        )
    else:
        options_telechargement.update(
            {
                "format": "bestaudio",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "0",
                    }
                ],
                "ffmpeg_location": get_ffmpeg_path(),
            }
        )

    return options_telechargement


def telecharger_avec_ydl(url: str, options: dict) -> None:
    with YoutubeDL(options) as ydl:
        ydl.download([url])


class DownloadManager:
    def __init__(self, on_update, telecharger=telecharger_avec_ydl):
        self._telechargements = []
        self.dossier_destination = os.getcwd()
        self.cookies_file = None
        self._on_update = on_update
        self._telecharger = telecharger

    def set_folder(self, dossier):
        self.dossier_destination = dossier

    def set_cookies(self, chemin):
        self.cookies_file = chemin

    def clear_cookies(self):
        self.cookies_file = None

    def add(self, url, format_media):
        identifiant_item = len(self._telechargements)
        self._telechargements.append(
            {"url": url, "format_media": format_media, "id": identifiant_item}
        )
        return identifiant_item

    def start(self):
        threading.Thread(target=self._run_all, daemon=True).start()

    def _run_all(self):
        total = len(self._telechargements)

        for index, telechargement in enumerate(self._telechargements):
            url = telechargement["url"]
            format_media = telechargement["format_media"]
            identifiant_item = telechargement["id"]

            self._on_update(identifiant_item, "⏳ Démarrage", index / total)

            def rappel_progression(informations_progression, iid=identifiant_item):
                if informations_progression["status"] == "downloading":
                    octets_recus = informations_progression.get("downloaded_bytes", 0)
                    octets_totaux = (
                        informations_progression.get("total_bytes")
                        or informations_progression.get("total_bytes_estimate")
                        or 1
                    )
                    self._on_update(
                        iid, "⬇️ Téléchargement", octets_recus / octets_totaux
                    )
                elif informations_progression["status"] == "finished":
                    self._on_update(iid, "🔄 Conversion...", 1)

            options_telechargement = build_ydl_opts(
                url,
                format_media,
                self.dossier_destination,
                self.cookies_file,
                rappel_progression,
            )

            try:
                self._telecharger(url, options_telechargement)
                self._on_update(identifiant_item, "✔️ Terminé", (index + 1) / total)
            except Exception as erreur:
                self._on_update(identifiant_item, f"❌ Erreur: {erreur}", index / total)
