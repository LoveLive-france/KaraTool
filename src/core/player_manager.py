import vlc
import os
from pathlib import Path


class PlayerManager:
    def __init__(self):
        self.instance = vlc.Instance(
            "--no-video-title-show", "--input-fast-seek", "--clock-jitter=0"
        )
        self.player = self.instance.media_player_new()

    def load_media(
        self, image_path, audio_path=None, subtitle_path=None, duration=None
    ):
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

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def set_volume(self, value):
        self.player.audio_set_volume(int(value))
