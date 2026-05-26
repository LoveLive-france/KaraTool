import vlc
import os
from pathlib import Path

class PlayerManager:
    def __init__(self):
        # On ne garde que le strict nécessaire pour la stabilité
        self.instance = vlc.Instance("--no-video-title-show", "--input-fast-seek")
        self.player = self.instance.media_player_new()

    def load_media(self, image_path, audio_path, subtitle_path=None, duration=None):
        self.player.stop()

        abs_image_path = str(Path(image_path).absolute())
        options = []
        
        # C'EST ICI LA CLÉ :
        # On dit à VLC de garder l'image affichée pendant la durée du morceau
        if duration:
            options.append(f":image-duration={int(duration) + 1}") # +1 pour la sécurité
        
        # Attachement audio
        audio_uri = Path(audio_path).absolute().as_uri()
        options.append(f":input-slave={audio_uri}")
        
        # Sous-titres
        if subtitle_path and os.path.exists(subtitle_path):
            abs_sub_path = str(Path(subtitle_path).absolute())
            options.append(f":sub-file={abs_sub_path}")
            
        media = self.instance.media_new(abs_image_path, *options)
        self.player.set_media(media)

    def attach_window(self, handle):
        if os.name == "nt":
            self.player.set_hwnd(handle)
        else:
            self.player.set_xwindow(handle)

    def play(self): self.player.play()
    def pause(self): self.player.pause()
    def stop(self): self.player.stop()
    def set_volume(self, value): self.player.audio_set_volume(int(value))