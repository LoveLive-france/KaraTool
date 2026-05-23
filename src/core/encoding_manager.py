import os
import sys
import threading
import subprocess
import json


def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.getcwd()


def encode_video(
    input_file,
    output_file,
    video_bitrate=4000,
    audio_bitrate=256,
    progress_callback=None,
):
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
        # optionnel mais important pour stabilité bitrate
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
        cmd += ["-c:a", "aac", "-b:a", f"{audio_bitrate}k"]

    cmd.append(output_file)

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
    )

    while True:
        line = process.stderr.readline()
        if not line:
            break

        if "time=" in line and progress_callback:
            progress_callback(line)

    process.wait()
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
    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        data = json.loads(result.stdout)
        return data["streams"][0]["codec_name"] == "opus"
    except Exception:
        return False


class EncodingManager:
    def __init__(self, on_update):
        self.queue = []
        self.output_folder = os.getcwd()
        self.on_update = on_update

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
            output_file = os.path.join(self.output_folder, f"{base}_x265.mp4")

            def progress(line):
                # ultra simple (tu peux améliorer après)
                self.on_update(item_id, "🔄 Encodage...", None)

            try:
                code = encode_video(input_file, output_file, progress)

                if code == 0:
                    self.on_update(item_id, "✔️ Terminé", (i + 1) / total)
                else:
                    self.on_update(item_id, "❌ Erreur FFmpeg", i / total)

            except Exception as e:
                self.on_update(item_id, f"❌ Exception: {e}", i / total)
