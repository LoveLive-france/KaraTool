import os
import io
import re
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from core.player_manager import PlayerManager
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TabLecteur(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self._manager = PlayerManager()

        self.video_path = None
        self.subtitle_path = None

        self.ass_events = []
        self.sub_running = False

        self.root = self.winfo_toplevel()

        # =========================
        # VIDEO FRAME
        # =========================
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.video_frame.bind("<Configure>", self._resize_album_art)
        self.video_frame.bind("<Button-1>", lambda e: self.root.focus_set())

        # =========================
        # SUBTITLE LABEL
        # =========================
        self.subtitle_label = ctk.CTkLabel(
            self.video_frame,
            text="",
            font=("Arial", 24),
            text_color="white",
            wraplength=900,
            justify="center"
        )

        self.subtitle_label.place(relx=.5, rely=.92, anchor="center")

        # =========================
        # CONTROLS
        # =========================
        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(controls, text="Lecture", command=self._manager.play).pack(side="left", padx=5)
        ctk.CTkButton(controls, text="Pause", command=self._manager.pause).pack(side="left", padx=5)
        ctk.CTkButton(controls, text="Stop", command=self._manager.stop).pack(side="left", padx=5)

        ctk.CTkButton(controls, text="Ouvrir média", command=self.open_video).pack(side="left", padx=10)
        ctk.CTkButton(controls, text="Sous-titres", command=self.open_subtitles).pack(side="left", padx=10)

        self.volume_slider = ctk.CTkSlider(
            controls,
            from_=0,
            to=100,
            command=self.set_volume
        )
        self.volume_slider.set(80)
        self.volume_slider.pack(side="right", padx=10)

        # =========================
        # KEYBOARD
        # =========================
        self.root.bind("<KeyPress>", self.on_key)

        self.after(150, lambda: self.root.focus_set())
        self.after(150, self.setup_video)

    # =========================================================
    # VLC
    # =========================================================
    def setup_video(self):
        handle = self.video_frame.winfo_id()
        self._manager.attach_window(handle)

    # =========================================================
    # FILES
    # =========================================================
    def open_video(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Media", "*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.flac *.ogg *.aac *.opus"),
                ("All", "*.*")
            ]
        )
        if path:
            self.video_path = path
            self.reload_media()

    def open_subtitles(self):
        path = filedialog.askopenfilename(
            filetypes=[("ASS subtitles", "*.ass")]
        )
        if path:
            self.subtitle_path = path
            self.reload_media()

    # =========================================================
    # MEDIA
    # =========================================================
    def reload_media(self):

        if not self.video_path:
            return

        self.subtitle_label.configure(text="")
        self.ass_events = []
        self.sub_running = False

        self._manager.load_media(self.video_path, self.subtitle_path)

        self.setup_video()

        if self.is_audio_file(self.video_path):
            self.after(100, lambda: self.show_album_art_from_file(self.video_path))

            if self.subtitle_path:
                self.load_ass_file()

    def is_audio_file(self, path):
        return path.lower().endswith(
            (".mp3", ".wav", ".flac", ".aac", ".ogg", ".opus")
        )

    # =========================================================
    # ALBUM ART
    # =========================================================
    def show_album_art_from_file(self, path):

        img_bytes = self.get_album_art(path)
        if not img_bytes:
            return

        image = Image.open(io.BytesIO(img_bytes))
        self._album_pil = image

        w = max(300, self.video_frame.winfo_width())
        h = max(300, self.video_frame.winfo_height())

        image = image.resize((w, h))

        self.album_img = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(w, h)
        )

        if hasattr(self, "album_label"):
            self.album_label.configure(image=self.album_img)
        else:
            self.album_label = ctk.CTkLabel(
                self.video_frame,
                image=self.album_img,
                text=""
            )
            self.album_label.place(relx=.5, rely=.5, anchor="center")

    def get_album_art(self, path):
        audio = MP3(path, ID3=ID3)

        if audio.tags is None:
            return None

        for tag in audio.tags.values():
            if tag.FrameID == "APIC":
                return tag.data

        return None

    # =========================================================
    # ASS PARSER (ROBUSTE SANS LIB EXTERNE)
    # =========================================================
    def load_ass_file(self):

        try:
            with open(self.subtitle_path, encoding="utf-8-sig") as f:
                lines = f.readlines()

            self.ass_events = []

            in_events = False

            for line in lines:

                line = line.strip()

                if line.startswith("[Events]"):
                    in_events = True
                    continue

                if not in_events:
                    continue

                if line.startswith("Dialogue:"):

                    parts = line.split(",", 9)

                    if len(parts) < 10:
                        continue

                    start = self._ass_time_to_ms(parts[1])
                    end = self._ass_time_to_ms(parts[2])
                    text = parts[9]

                    self.ass_events.append({
                        "start": start,
                        "end": end,
                        "text": text
                    })

            if not self.sub_running:
                self.sub_running = True
                self.update_subtitles()

        except Exception as e:
            print("ASS error:", e)

    def _ass_time_to_ms(self, t):

        # format: H:MM:SS.xx
        try:
            h, m, s = t.split(":")
            s, cs = s.split(".")

            return (
                int(h) * 3600000 +
                int(m) * 60000 +
                int(s) * 1000 +
                int(cs) * 10
            )

        except:
            return 0

    def update_subtitles(self):

        if not self.ass_events:
            self.after(100, self.update_subtitles)
            return

        current = self._manager.player.get_time()

        text = ""

        for ev in self.ass_events:

            if ev["start"] <= current <= ev["end"]:

                text = ev["text"]
                text = text.replace("\\N", "\n")
                text = re.sub(r"\{.*?\}", "", text)
                break

        self.subtitle_label.configure(text=text)

        self.after(100, self.update_subtitles)

    # =========================================================
    # CONTROLS
    # =========================================================
    def set_volume(self, value):
        self._manager.set_volume(value)

    def toggle_play(self):
        if self._manager.player.is_playing():
            self._manager.pause()
        else:
            self._manager.play()

    def seek(self, offset_ms):
        current = self._manager.player.get_time()
        self._manager.player.set_time(max(0, current + offset_ms))

    def change_volume(self, delta):
        current = self._manager.player.audio_get_volume()
        new = max(0, min(100, current + delta))
        self._manager.player.audio_set_volume(new)
        self.volume_slider.set(new)

    # =========================================================
    # KEYBOARD
    # =========================================================
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

    def _resize_album_art(self, event):
        if not hasattr(self, "_album_pil"):
            return

        if not hasattr(self, "album_label"):
            return

        w = max(100, event.width)
        h = max(100, event.height)

        img = self._album_pil.copy()
        img.thumbnail((w, h))

        self.album_img = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(img.width, img.height)
        )

        self.album_label.configure(image=self.album_img)