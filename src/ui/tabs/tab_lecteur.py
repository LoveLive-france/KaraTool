import os
import io
import tempfile
import customtkinter as ctk
from tkinter import filedialog
from core.player_manager import PlayerManager
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TabLecteur(ctk.CTkFrame):
    def __init__(self, parent):

        super().__init__(parent)

        self._manager = PlayerManager()

        self.media_path = None

        self.subtitle_path = None

        self.root = self.winfo_toplevel()

        self.video_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.video_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.video_frame.bind("<Button-1>", lambda e: self.root.focus_set())

        controls = ctk.CTkFrame(self)

        controls.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(controls, text="Lecture", command=self._manager.play).pack(
            side="left", padx=5
        )

        ctk.CTkButton(controls, text="Pause", command=self._manager.pause).pack(
            side="left", padx=5
        )

        ctk.CTkButton(controls, text="Stop", command=self._manager.stop).pack(
            side="left", padx=5
        )

        ctk.CTkButton(controls, text="Ouvrir média", command=self.open_media).pack(
            side="left", padx=10
        )

        ctk.CTkButton(controls, text="Sous-titres", command=self.open_subtitles).pack(
            side="left", padx=10
        )

        self.volume_slider = ctk.CTkSlider(
            controls, from_=0, to=100, command=self.set_volume
        )

        self.volume_slider.set(80)

        self.volume_slider.pack(side="right", padx=10)

        self.root.bind("<KeyPress>", self.on_key)

        self.after(150, lambda: self.root.focus_set())

    def setup_video(self):

        handle = self.video_frame.winfo_id()

        self._manager.attach_window(handle)

    def open_media(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Audio/Video", "*.mp3 *.wav *.flac *.mp4 *.mkv *.avi"),
                ("All", "*.*"),
            ]
        )

        if path:
            self.media_path = path

            self.reload_media()

    def open_subtitles(self):

        path = filedialog.askopenfilename(filetypes=[("ASS subtitles", "*.ass")])

        if path:
            self.subtitle_path = path

            self.reload_media()

    def get_audio_info(self, audio_path):

        temp_dir = tempfile.gettempdir()

        cover_path = os.path.join(temp_dir, "karaoke_temp_cover.png")

        duration = 300

        try:
            audio = MP3(audio_path, ID3=ID3)

            duration = audio.info.length

            if audio.tags:
                for tag in audio.tags.values():
                    if tag.FrameID == "APIC":
                        img = Image.open(io.BytesIO(tag.data))

                        img.save(cover_path)

                        return cover_path, duration

        except Exception as e:
            print("Erreur d'extraction :", e)

            pass

        # S'il n'y a pas d'image dans le MP3, on génère un fond noir

        img = Image.new("RGB", (1920, 1080), color="black")

        img.save(cover_path)

        return cover_path, duration

    def reload_media(self):
        if not self.media_path:
            return

        # On récupère l'extension pour savoir si c'est de l'audio ou de la vidéo
        ext = os.path.splitext(self.media_path)[1].lower()

        if ext in [".mp3", ".wav", ".flac"]:
            # 1. On extrait la cover (ou le fond noir) et la durée de l'audio
            cover_path, duration = self.get_audio_info(self.media_path)

            # 2. On passe les bons arguments : image, audio, sous-titres et durée
            self._manager.load_media(
                image_path=cover_path,
                audio_path=self.media_path,
                subtitle_path=self.subtitle_path,
                duration=duration,
            )
        else:
            # Si c'est une vidéo, le média principal est le fichier lui-même, pas d'audio esclave
            self._manager.load_media(
                image_path=self.media_path,
                audio_path=None,
                subtitle_path=self.subtitle_path,
            )

        # On attache la fenêtre une seule fois
        self.setup_video()

    def set_volume(self, value):

        self._manager.set_volume(value)

    def toggle_play(self):

        if self._manager.player.is_playing():
            self._manager.pause()

        else:
            self._manager.play()

    def seek(self, offset_ms):

        # Un seek simple, sans hack.

        # Si VLC est bien configuré (input-fast-seek), il gère la synchro.

        current = self._manager.player.get_time()

        if current != -1:
            self._manager.player.set_time(max(0, current + offset_ms))

    def force_subtitle_refresh(self):
        """Force VLC à recalculer le rendu des sous-titres sur la position actuelle"""

        # On récupère l'index de la piste active

        current_spu = self._manager.player.video_get_spu()

        # On désactive les sous-titres (cela vide le buffer de libass)

        self._manager.player.video_set_spu(-1)

        # On réactive (cela force libass à relire les tags .ass à l'instant T)

        self._manager.player.video_set_spu(current_spu)

    def change_volume(self, delta):

        current = self._manager.player.audio_get_volume()

        new = max(0, min(100, current + delta))

        self._manager.player.audio_set_volume(new)

        self.volume_slider.set(new)

    def adjust_subtitle_delay(self, delta_ms):

        current_delay_us = self._manager.player.video_get_spu_delay()

        new_delay_us = current_delay_us + (delta_ms * 1000)

        self._manager.player.video_set_spu_delay(new_delay_us)

        delay_ms = int(new_delay_us / 1000)

        self.delay_label.configure(text=f"Délai sous-titres : {delay_ms}ms")

    def on_key(self, event):

        key = event.keysym.lower()

        if key == "space":
            self.toggle_play()

        elif key == "left":
            self.seek(-5000)

        elif key == "right":
            self.seek(5000)

        elif key == "up":
            self.change_volume(5)

        elif key == "down":
            self.change_volume(-5)

        elif key == "s":
            self._manager.stop()

        elif key == "g":
            self.adjust_subtitle_delay(-100)

        elif key == "h":
            self.adjust_subtitle_delay(100)
