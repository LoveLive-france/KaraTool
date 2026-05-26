import vlc
import os
from pathlib import Path

class PlayerManager:
    def __init__(self):
        # On ne garde que le strict nécessaire pour la stabilité
        self.instance = vlc.Instance("--no-video-title-show", "--input-fast-seek")
        self.player = self.instance.media_player_new()

    def load_media(self, image_path, audio_path, subtitle_path=None):
        self.player.stop()

        # 1. On ouvre l'IMAGE comme média principal
        # Cela force VLC à créer un rendu vidéo
        abs_image_path = str(Path(image_path).absolute())
        
        # 2. On prépare les options
        options = []
        
        # On attache l'audio en "esclave" (input-slave)
        if audio_path:
            audio_uri = Path(audio_path).absolute().as_uri()
            options.append(f":input-slave={audio_uri}")
        
        # On attache les sous-titres
        if subtitle_path and os.path.exists(subtitle_path):
            abs_sub_path = str(Path(subtitle_path).absolute())
            options.append(f":sub-file={abs_sub_path}")
            
        # 3. Création du média (c'est l'image qui est le média principal)
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