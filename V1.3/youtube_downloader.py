import sys
import os
import customtkinter as ctk
from tkinter import filedialog
from tkinter import ttk
from yt_dlp import YoutubeDL
import subprocess
import threading
import os

# ---------- Import des binaries externes ----------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#YTDLP_PATH = resource_path("yt-dlp.exe")
#FFMPEG_PATH = resource_path("ffmpeg.exe")

#print("MEIPASS:", sys._MEIPASS if hasattr(sys, "_MEIPASS") else "NO MEIPASS")
#print("FILES:", os.listdir(sys._MEIPASS))

def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.getcwd()


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

downloads = []
download_folder = os.getcwd()
cookies_file = None

# ---------- UI ----------
app = ctk.CTk()
app.geometry("1000x650")
app.title("YouTube Downloader")

# Responsive grid config
app.grid_rowconfigure(1, weight=1)
app.grid_columnconfigure(0, weight=1)

# ---------- HEADER ----------
header = ctk.CTkFrame(app, height=70)
header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
header.grid_columnconfigure(0, weight=1)

title = ctk.CTkLabel(
    header,
    text="YouTube Downloader",
    font=("Arial", 24, "bold")
)
title.grid(row=0, column=0, padx=10, pady=10, sticky="w")


# ---------- INPUT BAR ----------
input_frame = ctk.CTkFrame(app)
input_frame.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 10))
input_frame.grid_columnconfigure(0, weight=1)

url_entry = ctk.CTkEntry(input_frame, placeholder_text="Lien")
url_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

format_var = ctk.StringVar(value="Vidéo")

format_menu = ctk.CTkOptionMenu(
    input_frame,
    values=["Vidéo", "Audio"],
    variable=format_var
)
format_menu.grid(row=0, column=1, padx=10)

# ---------- LIST AREA ----------
list_frame = ctk.CTkScrollableFrame(app)
list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
app.grid_rowconfigure(2, weight=1)

cards = {}


def create_card(item_id, url, fmt):
    card = ctk.CTkFrame(list_frame, corner_radius=12)
    card.pack(fill="x", padx=10, pady=8)

    left = ctk.CTkFrame(card)
    left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    title_lbl = ctk.CTkLabel(left, text=url, anchor="w")
    title_lbl.pack(fill="x")

    status_lbl = ctk.CTkLabel(left, text="⏳ En attente")
    status_lbl.pack(anchor="w", pady=5)

    progress = ctk.CTkProgressBar(card, width=150)
    progress.pack(side="right", padx=10)
    progress.set(0)

    cards[item_id] = {
        "status": status_lbl,
        "progress": progress
    }


def update_card(item_id, status=None, prog=None):
    card = cards.get(item_id)
    if not card:
        return

    if status:
        # texte
        card["status"].configure(text=status)

        # 🎨 couleur du texte selon statut
        if "✔️" in status:
            card["status"].configure(text_color="green")
        elif "❌" in status:
            card["status"].configure(text_color="red")
        elif "⬇️" in status:
            card["status"].configure(text_color="cyan")
        else:
            card["status"].configure(text_color="gray")

    if prog is not None:
        card["progress"].set(prog)


# ---------- ACTIONS ----------
def choose_folder():
    global download_folder
    folder = filedialog.askdirectory()
    if folder:
        download_folder = folder


def add_link():
    url = url_entry.get().strip()
    if not url:
        return

    fmt = format_var.get()

    item_id = len(downloads)

    downloads.append({
        "url": url,
        "fmt": fmt,
        "id": item_id
    })

    create_card(item_id, url, fmt)

    url_entry.delete(0, "end")


def run_download():
    total = len(downloads)

    def hook(d, item_id):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            progress = downloaded / total_bytes

            update_card(item_id, "⬇️ Téléchargement", progress)

        elif d['status'] == 'finished':
            update_card(item_id, "🔄 Conversion...", 1)

    for i, d in enumerate(downloads):
        url = d["url"]
        fmt = d["fmt"]
        item_id = d["id"]

        update_card(item_id, "⏳ Démarrage", i / total)

        ydl_opts = {
            "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [lambda x, item_id=item_id: hook(x, item_id)],
        }

        if cookies_file and os.path.exists(cookies_file):
            ydl_opts["cookiefile"] = cookies_file

        if fmt == "Vidéo":
            ydl_opts.update({
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "ffmpeg_location": get_ffmpeg_path(),
            })
        else:
            ydl_opts.update({
                "format": "bestaudio",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "0",
                }],
            })

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            update_card(item_id, "✔️ Terminé", (i + 1) / total)

        except Exception as e:
            update_card(item_id, f"❌ Erreur: {str(e)}", i / total)


def start_download():
    if not downloads:
        return

    threading.Thread(target=run_download, daemon=True).start()

def choose_cookies():
    global cookies_file
    file = filedialog.askopenfilename(filetypes=[("Cookies", "*.txt")])
    
    if file:
        cookies_file = file
        cookies_status_lbl.configure(
            text="● Cookies: chargés",
            text_color="green"
        )
    else:
        cookies_file = None
        cookies_status_lbl.configure(
            text="● Cookies: non chargés",
            text_color="red"
        )

def clear_cookies():
    global cookies_file
    cookies_file = None
    cookies_status_lbl.configure(
        text="● Cookies: non chargés",
        text_color="red"
    )

# ---------- FOOTER ----------
footer = ctk.CTkFrame(app)
footer.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

add_btn = ctk.CTkButton(footer, text="Ajouter", command=add_link)
add_btn.pack(side="left", padx=10)

folder_btn = ctk.CTkButton(footer, text="Dossier", command=choose_folder)
folder_btn.pack(side="left", padx=10)

start_btn = ctk.CTkButton(footer, text="Télécharger tout", command=start_download)
start_btn.pack(side="right", padx=10)

status_lbl = ctk.CTkLabel(footer, text="")
status_lbl.pack(side="right", padx=10)


cookies_status_lbl = ctk.CTkLabel(
    footer,
    text="",
    text_color="red",
    font=("Arial", 14, "bold")
)
cookies_status_lbl.pack(side="right", padx=10)

cookies_btn = ctk.CTkButton(footer, text="Cookies", command=choose_cookies)
cookies_btn.pack(side="left", padx=10)

clear_cookies_btn = ctk.CTkButton(footer, text="Vider cookies", command=clear_cookies)
clear_cookies_btn.pack(side="left", padx=10)

app.mainloop()
