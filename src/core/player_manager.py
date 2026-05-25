import vlc
import os

class PlayerManager:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

    def load_media(self, video_path, subtitle_path=None):
        self.player.stop()

        path = os.path.abspath(video_path)
        media = self.instance.media_new(path)

        if subtitle_path:
            subtitle_path = os.path.abspath(subtitle_path)
            media.add_option(f":sub-file={subtitle_path}")

        self.player.set_media(media)

        # IMPORTANT : on garde le renderer actif
        # PAS de set_hwnd(0) ici (sinon tu perds l’image album art UI cohérente)

        #self.player.play()

    def attach_window(self, handle):
        # attach uniquement si vidéo réelle
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