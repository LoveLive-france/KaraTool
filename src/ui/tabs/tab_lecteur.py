import os
import io
import tempfile
import ctypes
import customtkinter as ctk
from tkinter import filedialog
from core.player_manager import PlayerManager
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image
from pynput import mouse  # Ajout de pynput pour le scroll

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TabLecteur(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._manager = PlayerManager()
        self.media_path = None
        self.subtitle_path = None
        self.root = self.winfo_toplevel()
        self.is_fullscreen = False
        self.fs_window = None
        self.original_handle_parent = None

        self.video_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.video_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.video_frame.bind("<Button-1>", lambda e: self.root.focus_set())
        self.video_frame.bind("<Double-Button-1>", self.toggle_fullscreen)

        self.controls = ctk.CTkFrame(self)
        self.controls.pack(fill="x", padx=10, pady=10)

        icon_font = ctk.CTkFont(family="Courier New", size=22, weight="bold")
        ctk.CTkButton(
            self.controls,
            text="►",
            font=icon_font,
            width=40,
            command=self._manager.play,
        ).pack(side="left", padx=5)

        pause_font = ctk.CTkFont(family="Arial", size=20, weight="bold")
        ctk.CTkButton(
            self.controls,
            text="l l",
            font=pause_font,
            width=40,
            command=self._manager.pause,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.controls,
            text="■",
            font=icon_font,
            width=40,
            command=self._manager.stop,
        ).pack(side="left", padx=5)

        self.btn_media = ctk.CTkButton(
            self.controls, text="Ouvrir média", command=self.open_media
        )
        self.btn_media.pack(side="left", padx=10)

        self.btn_subtitles = ctk.CTkButton(
            self.controls, text="Sous-titres", command=self.open_subtitles
        )
        self.btn_subtitles.pack(side="left", padx=10)

        self.delay_label = ctk.CTkLabel(
            self.controls, text="Délai sous-titres : 0ms", text_color="gray"
        )
        self.delay_label.pack(side="right", padx=10)

        self.volume_slider = ctk.CTkSlider(
            self.controls, from_=0, to=100, command=self.set_volume
        )
        self.volume_slider.set(80)
        self.volume_slider.pack(side="right", padx=10)

        # Raccourcis claviers et souris classiques
        self.root.bind("<KeyPress>", self.on_key)
        self.root.bind("<MouseWheel>", self.on_mouse_wheel)
        self.root.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.after(150, lambda: self.root.focus_set())

        # --- DÉMARRAGE DE PYNPUT POUR LE SCROLL SUR LA VIDÉO ---
        self.mouse_listener = mouse.Listener(on_scroll=self._on_global_scroll)
        self.mouse_listener.start()

        # Arrêter le listener proprement si on détruit le widget
        self.bind("<Destroy>", lambda e: self.mouse_listener.stop())

    def setup_video(self):
        handle = self.video_frame.winfo_id()
        self._manager.attach_window(handle)
        self._manager.player.video_set_mouse_input(False)

    def open_media(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Audio/Video", "*.mp3 *.wav *.flac *.mp4 *.mkv *.avi"),
                ("All", "*.*"),
            ]
        )
        if path:
            self.media_path = path
            nom_fichier = os.path.basename(path)
            self.btn_media.configure(text=nom_fichier)
            self.reload_media()

    def open_subtitles(self):
        path = filedialog.askopenfilename(filetypes=[("ASS subtitles", "*.ass")])
        if path:
            self.subtitle_path = path
            nom_fichier = os.path.basename(path)
            self.btn_subtitles.configure(text=nom_fichier)
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

        img = Image.new("RGB", (1920, 1080), color="black")
        img.save(cover_path)
        return cover_path, duration

    def reload_media(self):
        if not self.media_path:
            return

        ext = os.path.splitext(self.media_path)[1].lower()
        if ext in [".mp3", ".wav", ".flac"]:
            cover_path, duration = self.get_audio_info(self.media_path)
            self._manager.load_media(
                image_path=cover_path,
                audio_path=self.media_path,
                subtitle_path=self.subtitle_path,
                duration=duration,
            )
        else:
            self._manager.load_media(
                image_path=self.media_path,
                audio_path=None,
                subtitle_path=self.subtitle_path,
            )
        self.setup_video()

    def set_volume(self, value):
        self._manager.set_volume(value)

    def toggle_play(self):
        if self._manager.player.is_playing():
            self._manager.pause()
        else:
            self._manager.play()

    def seek(self, offset_ms):
        current = self._manager.player.get_time()
        if current != -1:
            self._manager.player.set_time(max(0, current + offset_ms))

    def force_subtitle_refresh(self):
        current_spu = self._manager.player.video_get_spu()
        self._manager.player.video_set_spu(-1)
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

    def toggle_fullscreen(self, event=None):
        """Basculer en fullscreen"""
        if not self.is_fullscreen:
            self._enter_fullscreen()
        else:
            self._exit_fullscreen()

    def _enter_fullscreen(self):
        """Entrer en mode fullscreen VLC-like"""
        self.is_fullscreen = True
        handle = self.video_frame.winfo_id()

        # Masquer l'interface de l'app
        self.controls.pack_forget()

        # Créer fenêtre fullscreen noire
        self.fs_window = ctk.CTkToplevel(self.root)
        self.fs_window.attributes("-fullscreen", True)
        self.fs_window.configure(fg_color="black")

        # Renommer la fenêtre (utile pour Alt+Tab)
        if self.media_path:
            nom_video = os.path.basename(self.media_path)
            self.fs_window.title(f"{nom_video} - Plein écran")
        else:
            self.fs_window.title("Lecteur - Plein écran")

        self.fs_window.bind("<KeyPress>", self.on_key)
        self.fs_window.bind("<Double-Button-1>", self.toggle_fullscreen)
        self.fs_window.bind("<Escape>", lambda e: self._exit_fullscreen())
        self.fs_window.bind("<Button-1>", self.toggle_fullscreen)

        self.fs_window.update()

        # Sauvegarder le vrai parent natif
        self.original_handle_parent = ctypes.windll.user32.GetParent(handle)

        try:
            # Reparenter la vidéo dans la fenêtre fullscreen
            ctypes.windll.user32.SetParent(handle, self.fs_window.winfo_id())

            # Cacher l'application principale
            self.root.withdraw()

            # Forcer l'affichage de la vidéo (évite l'écran noir) et la redimensionner
            w = self.fs_window.winfo_screenwidth()
            h = self.fs_window.winfo_screenheight()

            ctypes.windll.user32.ShowWindow(handle, 5)  # 5 = SW_SHOW
            ctypes.windll.user32.MoveWindow(handle, 0, 0, w, h, True)

            self.fs_window.focus_set()
        except Exception as e:
            print(f"Erreur fullscreen: {e}")
            self.root.deiconify()
            self._exit_fullscreen()
            return

        self._manager.player.video_set_mouse_input(False)

    def _exit_fullscreen(self):
        """Quitter le mode fullscreen"""
        if not self.is_fullscreen:
            return

        self.is_fullscreen = False
        handle = self.video_frame.winfo_id()

        try:
            # 1. Faire réapparaître l'application en premier
            self.root.deiconify()
            self.controls.pack(fill="x", padx=10, pady=10)

            # 2. Restaurer le parent d'origine de la vidéo
            if self.original_handle_parent:
                ctypes.windll.user32.SetParent(handle, self.original_handle_parent)

            self.update_idletasks()
            self.video_frame.update_idletasks()

            # 3. Récupérer les dimensions du conteneur Tkinter
            video_x = self.video_frame.winfo_x()
            video_y = self.video_frame.winfo_y()
            video_w = self.video_frame.winfo_width()
            video_h = self.video_frame.winfo_height()

            # 4. Fonction pour repositionner et forcer la visibilité
            def restore_video_view():
                ctypes.windll.user32.MoveWindow(
                    handle, video_x, video_y, video_w, video_h, True
                )
                ctypes.windll.user32.ShowWindow(handle, 5)

            if video_w > 0 and video_h > 0:
                self.after(50, restore_video_view)

            # 5. Détruire la fenêtre fullscreen
            if hasattr(self, "fs_window") and self.fs_window:
                try:
                    self.fs_window.destroy()
                except Exception:
                    pass
                self.fs_window = None

            # 6. Réattacher VLC
            self._manager._appliquer_attach_window(handle)

        except Exception as e:
            print(f"Erreur exit fullscreen: {e}")
            self.root.deiconify()
        finally:
            self.root.focus_set()

        self._manager.player.video_set_mouse_input(False)

    def on_key(self, event):
        """Gérer les événements clavier"""
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
        elif key == "f":
            self.toggle_fullscreen()
        elif key == "escape" and self.is_fullscreen:
            self._exit_fullscreen()

    def on_mouse_wheel(self, event):
        """Gérer la molette souris classique Tkinter (quand on survole l'UI)"""
        # On ignore si on est en fullscreen (pynput s'en occupe)
        if self.is_fullscreen:
            return

        if event.delta > 0:
            self.change_volume(5)
        elif event.delta < 0:
            self.change_volume(-5)

    def _on_global_scroll(self, x, y, dx, dy):
        """Gérer la molette de la souris au-dessus de la vidéo (via pynput)"""
        target = (
            self.fs_window
            if self.is_fullscreen and self.fs_window
            else self.video_frame
        )

        if target and target.winfo_exists() and target.winfo_viewable():
            try:
                wx = target.winfo_rootx()
                wy = target.winfo_rooty()
                ww = target.winfo_width()
                wh = target.winfo_height()

                # Vérifier si le curseur est dans la zone de la vidéo
                if wx <= x <= (wx + ww) and wy <= y <= (wy + wh):
                    # Déléguer l'exécution au thread de Tkinter pour éviter les blocages
                    if dy > 0:
                        self.after(0, lambda: self.change_volume(5))
                    elif dy < 0:
                        self.after(0, lambda: self.change_volume(-5))
            except Exception:
                pass  # Évite les crashs si Tkinter est en cours de redimensionnement
