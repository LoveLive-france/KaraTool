import os
import sys
import threading
import subprocess
import json
from collections import deque


def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.getcwd()


def encode_media(
    input_file,
    output_file,
    video_bitrate=4000,
    audio_bitrate=256,
    progress_callback=None,
):
    ext = os.path.splitext(input_file)[1].lower()
    is_audio = ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]

    if is_audio:
        bitrate_cbr = f"{audio_bitrate}k" if audio_bitrate else "320k"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-c:a",
            "opus",
            "-b:a",
            bitrate_cbr,
        ]
    else:
        audio_copy = has_opus_audio(input_file)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-c:v",
            "libx265",
            "-preset",
            "fast",
            "-b:v",
            f"{video_bitrate}k",
            "-maxrate",
            f"{video_bitrate * 2}k",
            "-bufsize",
            f"{video_bitrate * 4}k",
            "-movflags",
            "+faststart",
        ]
        if audio_copy:
            cmd += ["-c:a", "copy"]
        else:
            cmd += ["-c:a", "libopus", "-b:a", f"{audio_bitrate}k"]

    cmd.append(output_file)

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
    )

    error_log = deque(maxlen=5)

    while True:
        line = process.stderr.readline()
        if not line:
            break

        clean_line = line.strip()
        if clean_line:
            error_log.append(clean_line)

        if "time=" in line and progress_callback:
            progress_callback(line)

    process.wait()

    if process.returncode != 0:
        detail_erreur = " | ".join(error_log) if error_log else "Erreur inconnue"
        raise RuntimeError(f"FFmpeg crash: {detail_erreur}")

    return process.returncode


def has_opus_audio(file):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "json",
        file,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return data["streams"][0]["codec_name"] == "opus"
    except Exception:
        return False


class EncodingManager:
    def __init__(self, on_update):
        self.queue = []
        self.output_folder = os.getcwd()
        self.on_update = on_update
        self.video_bitrate = 4000
        self.audio_bitrate = 256

    def set_bitrate_params(self, video_bitrate=4000, audio_bitrate=256):
        self.video_bitrate = video_bitrate
        self.audio_bitrate = audio_bitrate

    def set_folder(self, folder):
        self.output_folder = folder

    def add(self, input_file):
        item_id = len(self.queue)
        self.queue.append({"id": item_id, "input": input_file})
        return item_id

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        total = len(self.queue)

        for i, item in enumerate(self.queue):
            item_id = item["id"]
            input_file = item["input"]

            self.on_update(item_id, "⏳ Démarrage", i / total)

            base = os.path.splitext(os.path.basename(input_file))[0]
            ext = os.path.splitext(input_file)[1].lower()

            if ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]:
                output_file = os.path.join(self.output_folder, f"{base}_fixed_cbr.mp3")
            else:
                output_file = os.path.join(self.output_folder, f"{base}_x265.mp4")

            def progress(line):
                self.on_update(item_id, "🔄 Encodage...", None)

            try:
                encode_media(
                    input_file=input_file,
                    output_file=output_file,
                    video_bitrate=self.video_bitrate,
                    audio_bitrate=self.audio_bitrate,
                    progress_callback=progress,
                )
                self.on_update(item_id, "✔️ Terminé", (i + 1) / total)

            except RuntimeError as re:
                self.on_update(item_id, f"❌ {str(re)}", i / total)
            except Exception as e:
                self.on_update(item_id, f"❌ Exception: {str(e)}", i / total)
