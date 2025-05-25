#!/usr/bin/env python3

import os
import subprocess
import re
import threading
import tkinter as tk
from tkinter import filedialog, StringVar
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap import constants as TTKConst
from ytmusicapi import YTMusic

# Initialisation de l'API et des flags de contrôle
yt = YTMusic("headers_auth.json")
stop_flag = threading.Event()
pause_flag = threading.Event()

class Downloader:
    def __init__(self, dest_path, audio_format, bitrate, log_textbox, progress_playlist, progress_label_var, progress_track, progress_track_label):
        self.dest_path = dest_path
        self.audio_format = audio_format
        self.ext = "ogg" if audio_format == "vorbis" else audio_format
        self.bitrate = bitrate
        self.log_textbox = log_textbox
        self.progress_playlist = progress_playlist
        self.progress_label_var = progress_label_var
        self.progress_track = progress_track
        self.progress_track_label = progress_track_label

    def extract_playlist_id(self, line):
        match = re.search(r'list=([A-Za-z0-9_-]+)', line)
        return match.group(1) if match else line.strip()

    def sanitize_filename(self, name):
        return "".join(c if c.isalnum() or c in " -_()" else "_" for c in name)

    def log_message(self, message):
        self.log_textbox.insert(tk.END, message + "\n")
        self.log_textbox.see(tk.END)

    def stop_download(self):
        stop_flag.set()

    def pause_download(self):
        pause_flag.set()

    def resume_download(self):
        pause_flag.clear()

    def process_playlists(self, urls):
        stop_flag.clear()
        playlist_ids = [self.extract_playlist_id(url) for url in urls if url.strip()]
        total_playlists = len(playlist_ids)
        self.progress_playlist.configure(maximum=total_playlists)
        self.progress_playlist.configure(value=0)
        self.progress_label_var.set(f"0 / {total_playlists} playlists")

        for i, playlist_id in enumerate(playlist_ids):
            if stop_flag.is_set():
                self.log_message("[🛑] Téléchargement interrompu.")
                break
            try:
                playlist = yt.get_playlist(playlist_id)
            except Exception as e:
                self.log_message(f"[!] Erreur : {playlist_id} → {e}")
                continue

            playlist_name = self.sanitize_filename(playlist["title"])
            download_dir = os.path.join(self.dest_path, playlist_name)
            os.makedirs(download_dir, exist_ok=True)

            tracks = playlist["tracks"]
            self.progress_track.configure(maximum=len(tracks))
            self.progress_track.configure(value=0)

            threads = []
            for j, song in enumerate(tracks):
                if stop_flag.is_set():
                    self.log_message("[🛑] Téléchargement interrompu.")
                    return

                while pause_flag.is_set():
                    threading.Event().wait(0.5)
                
                thread = threading.Thread(target=self.download_track, args=(song, download_dir, j, len(tracks)))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            self.progress_playlist.configure(value=i+1)
            self.progress_label_var.set(f"{i+1} / {total_playlists} playlists")

        self.log_message("✅ Tous les téléchargements sont terminés.")

    def download_track(self, song, download_dir, track_index, total_tracks):
        title = song["title"]
        artist = song["artists"][0]["name"]
        video_id = song["videoId"]
        url = f"https://music.youtube.com/watch?v={video_id}"
        safe_filename = self.sanitize_filename(f"{artist} - {title}")
        output_path = os.path.join(download_dir, f"{safe_filename}.%(ext)s")
        final_path = output_path.replace("%(ext)s", self.ext)
        if os.path.exists(final_path):
            self.log_message(f"[✓] Déjà présent : {artist} - {title}.{self.ext}")
        else:
            self.log_message(f"[↓] Téléchargement : {artist} - {title}")
            try:
                subprocess.run([
                    "yt-dlp",
                    "--cookies", "ytmusic_cookies.txt",
                    "-f", "251",
                    "-x", "--audio-format", self.audio_format,
                    "--audio-quality", self.bitrate,
                    "--embed-thumbnail",
                    "--embed-metadata",
                    "--extractor-args", "youtube:player_client=tv",
                    "--output", output_path,
                    url
                ], check=True)
            except subprocess.CalledProcessError as e:
                self.log_message(f"[!] Erreur lors du téléchargement : {artist} - {title} → {e}")
        self.progress_track.configure(value=track_index+1)
        self.progress_track_label.set(f"{track_index+1} / {total_tracks} titres")

def start_download():
    if not dest_path_var.get():
        log_textbox.insert(tk.END, "[!] Choisis un dossier de destination d'abord.\n")
        return

    downloader = Downloader(
        dest_path_var.get(),
        format_var.get(),
        bitrate_var.get(),
        log_textbox,
        progress_playlist,
        progress_label_var,
        progress_track,
        progress_track_label
    )
    threading.Thread(
        target=downloader.process_playlists,
        args=(url_textbox.get("1.0", tk.END).strip().splitlines(),),
        daemon=True
    ).start()

def paste_playlist(event):
    try:
        clipboard_text = event.widget.clipboard_get()
    except Exception:
        clipboard_text = ""
    if clipboard_text:
        event.widget.insert(tk.END, clipboard_text + "\n")
    return "break"

def create_gui():
    global url_textbox, log_textbox, progress_playlist, progress_label_var
    global dest_path_var, format_var, bitrate_var, progress_track, progress_track_label

    # Création de la fenêtre avec ttkbootstrap en mode sombre (thème "darkly")
    window = ttk.Window(themename="darkly")
    window.title("Téléchargeur YouTube Music")
    window.geometry("850x750")
    
    # Cadre pour les entrées d'URL
    frm_top = ttk.Frame(window, padding=10)
    frm_top.pack(fill="x")
    lbl_info = ttk.Label(frm_top, text="Colle ici les liens ou IDs de playlists (1 par ligne)")
    lbl_info.pack(anchor="w", pady=5)
    url_textbox = tk.Text(frm_top, height=6, wrap="word", font=("Helvetica", 10))
    url_textbox.pack(fill="x", padx=5, pady=5)
    url_textbox.bind("<Button-3>", paste_playlist)

    # Cadre pour le dossier de destination
    frm_dest = ttk.Frame(window, padding=10)
    frm_dest.pack(fill="x")
    dest_path_var = StringVar()
    ent_dest = ttk.Entry(frm_dest, textvariable=dest_path_var, width=60)
    ent_dest.pack(side="left", padx=(0, 10))
    btn_browse = ttk.Button(frm_dest, text="Parcourir", command=lambda: dest_path_var.set(filedialog.askdirectory()))
    btn_browse.pack(side="left")

    # Cadre pour les options de format et de bitrate
    frm_options = ttk.Frame(window, padding=10)
    frm_options.pack(fill="x")
    format_var = StringVar(value="vorbis")
    lbl_format = ttk.Label(frm_options, text="Format:")
    lbl_format.pack(side="left", padx=(0, 5))
    opt_format = ttk.OptionMenu(frm_options, format_var, "vorbis", "mp3", "flac", "aac", "m4a", "opus", "wav", "alac")
    opt_format.pack(side="left", padx=(0, 20))
    bitrate_var = StringVar(value="320k")
    lbl_bitrate = ttk.Label(frm_options, text="Bitrate:")
    lbl_bitrate.pack(side="left", padx=(0,5))
    opt_bitrate = ttk.OptionMenu(frm_options, bitrate_var, "320k", "192k", "128k")
    opt_bitrate.pack(side="left")

    # Cadre pour les barres de progression
    frm_progress = ttk.Frame(window, padding=10)
    frm_progress.pack(fill="x")
    progress_label_var = StringVar(value="0 / 0 playlists")
    lbl_progress = ttk.Label(frm_progress, textvariable=progress_label_var)
    lbl_progress.pack(anchor="w")
    progress_playlist = ttk.Progressbar(frm_progress, length=700, mode="determinate")
    progress_playlist.pack(pady=(0, 10))
    progress_track_label = StringVar(value="0 / 0 titres")
    lbl_track = ttk.Label(frm_progress, textvariable=progress_track_label)
    lbl_track.pack(anchor="w")
    progress_track = ttk.Progressbar(frm_progress, length=700, mode="determinate")
    progress_track.pack()

    # Cadre pour la zone de log
    frm_log = ttk.Frame(window, padding=10)
    frm_log.pack(fill="both", expand=True)
    log_textbox = ScrolledText(frm_log, bootstyle="default", wrap="word", height=12, font=("Helvetica", 10))
    log_textbox.pack(fill="both", expand=True, pady=5)

    # Cadre pour les boutons de commande
    frm_buttons = ttk.Frame(window, padding=10)
    frm_buttons.pack()
    btn_download = ttk.Button(frm_buttons, text="Télécharger", command=start_download, bootstyle=TTKConst.SUCCESS)
    btn_download.pack(side="left", padx=5)
    btn_pause = ttk.Button(frm_buttons, text="Pause", command=lambda: pause_flag.set(), bootstyle=TTKConst.WARNING)
    btn_pause.pack(side="left", padx=5)
    btn_resume = ttk.Button(frm_buttons, text="Reprendre", command=lambda: pause_flag.clear(), bootstyle=TTKConst.INFO)
    btn_resume.pack(side="left", padx=5)
    btn_stop = ttk.Button(frm_buttons, text="🛑 Stop", command=lambda: stop_flag.set(), bootstyle=TTKConst.DANGER)
    btn_stop.pack(side="left", padx=5)

    window.mainloop()

if __name__ == "__main__":
    create_gui()

