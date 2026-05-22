import os
import sys
import threading
from yt_dlp import YoutubeDL


def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.getcwd()


def build_ydl_opts(url, fmt, download_folder, cookies_file=None, hook=None):
    opts = {
        "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    if hook:
        opts["progress_hooks"] = [hook]

    if cookies_file:
        opts["cookiefile"] = cookies_file

    if fmt == "Vidéo":
        opts.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "ffmpeg_location": get_ffmpeg_path(),
        })
    else:
        opts.update({
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            }],
            "ffmpeg_location": get_ffmpeg_path(),
        })

    return opts


class DownloadManager:
    def __init__(self, on_update):
        self._downloads = []
        self.download_folder = os.getcwd()
        self.cookies_file = None
        self._on_update = on_update  # callback(item_id, status, progress)

    def set_folder(self, folder):
        self.download_folder = folder

    def set_cookies(self, path):
        self.cookies_file = path

    def clear_cookies(self):
        self.cookies_file = None

    def add(self, url, fmt):
        item_id = len(self._downloads)
        self._downloads.append({"url": url, "fmt": fmt, "id": item_id})
        return item_id

    def start(self):
        threading.Thread(target=self._run_all, daemon=True).start()

    def _run_all(self):
        total = len(self._downloads)

        for i, d in enumerate(self._downloads):
            url = d["url"]
            fmt = d["fmt"]
            item_id = d["id"]

            self._on_update(item_id, "⏳ Démarrage", i / total)

            def hook(data, iid=item_id):
                if data["status"] == "downloading":
                    downloaded = data.get("downloaded_bytes", 0)
                    total_bytes = data.get("total_bytes") or data.get("total_bytes_estimate") or 1
                    self._on_update(iid, "⬇️ Téléchargement", downloaded / total_bytes)
                elif data["status"] == "finished":
                    self._on_update(iid, "🔄 Conversion...", 1)

            opts = build_ydl_opts(url, fmt, self.download_folder, self.cookies_file, hook)

            try:
                with YoutubeDL(opts) as ydl:
                    ydl.download([url])
                self._on_update(item_id, "✔️ Terminé", (i + 1) / total)
            except Exception as e:
                self._on_update(item_id, f"❌ Erreur: {e}", i / total)
