import os
import threading
import customtkinter as ctk
from tkinter import filedialog, Listbox
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from plyer import notification
import time
import yt_dlp

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("700x500")
        self.pause_event = threading.Event()
        self.download_history = []

        # Creating a tab view
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill='both')

        # Add tabs
        self.main_tab = self.tabview.add("Main")
        self.settings_tab = self.tabview.add("Settings")
        self.history_tab = self.tabview.add("History")

        # Main Tab
        self.download_type_label = ctk.CTkLabel(self.main_tab, text="Select Download Type:")
        self.download_type_label.pack(pady=10)

        self.download_type_options = ["Playlist", "Multiple Videos", "Single Video"]
        self.download_type_var = ctk.StringVar(value=self.download_type_options[0])
        self.download_type_menu = ctk.CTkOptionMenu(self.main_tab, variable=self.download_type_var, values=self.download_type_options, command=self.update_url_entry)
        self.download_type_menu.pack(pady=10)

        self.label = ctk.CTkLabel(self.main_tab, text="Enter URL(s):")
        self.label.pack(pady=10)

        self.url_entry = ctk.CTkEntry(self.main_tab, width=500)
        self.url_entry.pack(pady=10)

        self.output_folder_label = ctk.CTkLabel(self.main_tab, text="Select Output Folder:")
        self.output_folder_label.pack(pady=10)

        self.output_folder_entry = ctk.CTkEntry(self.main_tab, width=500)
        self.output_folder_entry.pack(pady=10)

        self.output_folder_button = ctk.CTkButton(self.main_tab, text="Browse", command=self.select_output_folder)
        self.output_folder_button.pack(pady=10)

        self.download_button = ctk.CTkButton(self.main_tab, text="Download", command=self.start_download)
        self.download_button.pack(pady=10)

        self.pause_button = ctk.CTkButton(self.main_tab, text="Pause", command=self.pause_download)
        self.pause_button.pack(pady=10)

        self.resume_button = ctk.CTkButton(self.main_tab, text="Resume", command=self.resume_download)
        self.resume_button.pack(pady=10)

        self.progress_label = ctk.CTkLabel(self.main_tab, text="")
        self.progress_label.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.main_tab, width=500)
        self.progress_bar.pack(pady=10)

        # Settings Tab
        self.quality_label = ctk.CTkLabel(self.settings_tab, text="Select Quality:")
        self.quality_label.pack(pady=10)

        self.quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p"]
        self.quality_var = ctk.StringVar(value=self.quality_options[0])
        self.quality_menu = ctk.CTkOptionMenu(self.settings_tab, variable=self.quality_var, values=self.quality_options)
        self.quality_menu.pack(pady=10)

        self.fps_label = ctk.CTkLabel(self.settings_tab, text="Select FPS:")
        self.fps_label.pack(pady=10)

        self.fps_options = ["24", "30", "60"]
        self.fps_var = ctk.StringVar(value=self.fps_options[0])
        self.fps_menu = ctk.CTkOptionMenu(self.settings_tab, variable=self.fps_var, values=self.fps_options)
        self.fps_menu.pack(pady=10)

        self.format_label = ctk.CTkLabel(self.settings_tab, text="Select Format:")
        self.format_label.pack(pady=10)

        self.format_options = ["mp4", "h265", "audio"]
        self.format_var = ctk.StringVar(value=self.format_options[0])
        self.format_menu = ctk.CTkOptionMenu(self.settings_tab, variable=self.format_var, values=self.format_options)
        self.format_menu.pack(pady=10)

        self.custom_encoding_label = ctk.CTkLabel(self.settings_tab, text="Custom Encoding Options (optional):")
        self.custom_encoding_label.pack(pady=10)

        self.custom_encoding_entry = ctk.CTkEntry(self.settings_tab, width=500)
        self.custom_encoding_entry.pack(pady=10)

        # History Tab
        self.history_list = Listbox(self.history_tab)
        self.history_list.pack(pady=10, expand=True, fill='both')

    def update_url_entry(self, selection):
        if selection == "Multiple Videos":
            self.label.configure(text="Enter URLs (comma-separated):")
        else:
            self.label.configure(text="Enter URL:")

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_entry.delete(0, ctk.END)
            self.output_folder_entry.insert(0, folder_selected)

    def start_download(self):
        self.progress_label.configure(text="Starting download...")
        self.progress_bar.set(0)
        self.history_list.delete(0, ctk.END)
        threading.Thread(target=self.download).start()

    def download(self):
        download_type = self.download_type_var.get()
        urls = self.url_entry.get().split(',')
        output_folder = self.output_folder_entry.get()

        if download_type == "Playlist":
            self.download_playlist(urls[0].strip(), output_folder)
        elif download_type == "Multiple Videos":
            self.download_multiple_videos(urls, output_folder)
        elif download_type == "Single Video":
            self.download_single_video(urls[0].strip(), output_folder)

    def download_playlist(self, playlist_url, output_folder):
        ydl_opts = {
            'outtmpl': os.path.join(output_folder, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio',
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        self.progress_label.configure(text="Playlist download complete")
        self.notify_user("Playlist download complete")

    def download_multiple_videos(self, urls, output_folder):
        ydl_opts = {
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio',
            'merge_output_format': 'mp4',
        }
        for url in urls:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url.strip()])
        self.progress_label.configure(text="Multiple videos download complete")
        self.notify_user("Multiple videos download complete")

    def download_single_video(self, video_url, output_folder):
        ydl_opts = {
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio',
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        self.progress_label.configure(text="Single video download complete")
        self.notify_user("Single video download complete")

    def pause_download(self):
        self.pause_event.set()

    def resume_download(self):
        self.pause_event.clear()
        threading.Thread(target=self.download).start()

    def notify_user(self, message):
        notification.notify(
            title='YouTube Downloader',
            message=message,
            timeout=5
        )

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
