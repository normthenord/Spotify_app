import tkinter as tk
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from dotenv import load_dotenv
import os
import utility
import time
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

play_button = tk.Button(button_frame, text="Play", command=lambda: utility.play(sp))
play_button.pack(side="left")

pause_button = tk.Button(button_frame, text="Pause", command=lambda: utility.pause(sp))
pause_button.pack(side="left")

next_button = tk.Button(
    button_frame, text="Next", command=lambda: utility.next_song(sp))
next_button.pack(side="left")


shuffle_button = tk.Button(
    button_frame,
    text="Shuffle",
    command=lambda: utility.shuffle_switch(sp)
)
shuffle_button.pack(side="left")


#VOLUME SLIDER
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

# Search area
search_frame = tk.Frame(root)
search_frame.pack(fill="x", padx=10, pady=10)


album_ids = []
track_ids = []

search_entry = tk.Entry(search_frame)
search_entry.pack(side="left", fill="x", expand=True)

search_entry.bind("<Return>", lambda event: utility.search_albums(
    search_entry, sp, playlist_listbox, album_ids))

search_button = tk.Button(
    search_frame,
    text="Search",
    command=lambda: utility.search_albums(
        search_entry, sp, playlist_listbox, album_ids)
)


search_button.pack(side="left", padx=5)

# Results list
playlist_listbox = tk.Listbox(root)
playlist_listbox.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


playlist_listbox.bind(
    "<<ListboxSelect>>",
    lambda event: utility.album_selected(event, sp, album_ids, track_ids, track_listbox)
)

track_listbox = tk.Listbox(root)
track_listbox.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

track_listbox.bind(
    "<<ListboxSelect>>",
    lambda event: utility.track_selected(event, sp, album_ids, track_ids, playlist_listbox)
)

root.mainloop()

# utility.pause(sp)
