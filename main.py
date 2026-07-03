import time

import tkinter as tk
from tkinter import ttk
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from dotenv import load_dotenv
import os
import utility
import threading
playlist_id = "7KHdtsSrAhhQUQIVHTgq4t"

load_dotenv()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


sp = Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri="https://127.0.0.1:8888/callback",
        scope="user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative"
    ))

root = tk.Tk()
root.title("Spotify")

button_frame = tk.Frame(root)
button_frame.pack()

play_button = tk.Button(button_frame, text="Play",
                        command=lambda: utility.play(sp))
play_button.pack(side="left")

pause_button = tk.Button(button_frame, text="Pause",
                         command=lambda: utility.pause(sp))
pause_button.pack(side="left")

next_button = tk.Button(
    button_frame, text="Next", command=lambda: utility.next_song(sp))
next_button.pack(side="left")


shuffle_button = tk.Button(
    button_frame,
    text="Shuffle",
    command=lambda: utility.shuffle_switch(sp, shuffle_button)
)
shuffle_button.pack(side="left")


class Toggles:
    play = play_button
    shuffle = shuffle_button


toggles = Toggles()


# VOLUME SLIDER
volume_slider = tk.Scale(
    root,
    from_=0,
    to=100,
    orient=tk.HORIZONTAL,
    length=300,
    label="Volume"
)
original_volume = sp.current_playback()["device"]["volume_percent"]
volume_slider.set(original_volume)
volume_slider.pack(fill="x", padx=10)
volume_slider.bind("<ButtonRelease-1>",
                   lambda event: utility.volume_released(event, volume_slider, sp))


class Sliders:
    volume_slider = original_volume


# Search area
search_frame = tk.Frame(root)
search_frame.pack(fill="x", padx=10, pady=10)


album_ids = []
track_ids = []

search_entry = tk.Entry(search_frame)
search_entry.pack(side="left", fill="x", expand=True)

search_entry.bind("<Return>", lambda event: utility.search_albums(
    search_entry, sp, album_listbox, album_ids))

search_button = tk.Button(
    search_frame,
    text="Search",
    command=lambda: utility.search_albums(
        search_entry, sp, album_listbox, album_ids)
)


search_button.pack(side="left", padx=5)

# Results list
album_listbox = tk.Listbox(root)
album_listbox.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

selected_album_id = [None]
album_listbox.bind(
    "<<ListboxSelect>>",
    lambda event: utility.album_selected(
        event, sp, album_ids, track_ids, track_listbox, album_id=selected_album_id)
)



######SONG INFO AND ALBUM ART

song_info_frame = tk.Frame(root)
song_info_frame.pack(fill="x", pady=0, padx=20)

text_frame = tk.Frame(song_info_frame)
text_frame.pack(side="left", anchor="n")

song_label = tk.Label(text_frame, text="Song Title")
song_label.pack(anchor="center")

album_label = tk.Label(text_frame, text="Album Name")
album_label.pack(anchor="center")

album_art = tk.Label(song_info_frame, image=None)

album_art.pack(side="right", padx=20, pady=0, anchor="center")


progress_frame = tk.Frame(root)
progress_frame.pack(fill="x", padx=20, pady=5)

elapsed_label = tk.Label(progress_frame, text="0:00", width=5, anchor="e")
elapsed_label.pack(side="left")


track_pb: ttk.Progressbar = ttk.Progressbar(progress_frame, mode="determinate")
track_pb.pack(
    side="left",
    fill="x",
    padx="8",
    expand=True
)

duration_label = tk.Label(progress_frame, text="0:00", width=5, anchor="w")
duration_label.pack(side="left")

progress_bar = {"elapsed_label": elapsed_label,
                "track_pb": track_pb, "duration_label": duration_label}

track_listbox = tk.Listbox(root)
track_listbox.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

track_listbox.bind(
    "<<ListboxSelect>>",
    lambda event: utility.track_selected(
        event, sp, album_id=selected_album_id, track_ids=track_ids, progress_bar=progress_bar)
)


class Song_Labels:
    name_and_artist = None,
    album = None,
    album_art = None


song_labels = Song_Labels()
song_labels.name_and_artist = song_label
song_labels.album = album_label
song_labels.album_art = album_art


def update_playback():
    while True:
        utility.update(sp, progress_bar, song_labels, toggles)
        time.sleep(0.5)


threading.Thread(target=update_playback, daemon=True).start()



root.mainloop()
