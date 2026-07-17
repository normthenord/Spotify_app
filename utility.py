from dataclasses import dataclass
import tkinter as tk
import requests
from io import BytesIO
from PIL import Image, ImageTk


def next_song(sp):
    sp.next_track()


def pick_playlist(sp):
    print("Search for a playlist")
    artist = input()
    results = sp.search(artist, type="playlist")

    playlists = results["playlists"]["items"]

    potential_playlist = []

    for playlist in playlists:
        if playlist is not None:
            if playlist["items"]["total"] >= 60:
                potential_playlist.append(playlist)

    print("Pick one:")
    for i, playlist in enumerate(potential_playlist):
        print(f"{i + 1}: {playlist['name']}")

    print("Enter the number of the playlist you want to use:")
    choice = int(input()) - 1

    playlist_id = potential_playlist[choice]["id"]

    print(f"You chose: {potential_playlist[choice]['name']}")

    sp.start_playback(context_uri=f"spotify:playlist:{playlist_id}")


def volume_released(event, volume_slider, sp):
    volume = volume_slider.get()
    print(f"Volume set to: {volume}")
    change_volume(sp, volume)


def change_volume(sp, volume):
    sp.volume(volume)


def play(sp):
    state = sp.current_playback()
    if not state or state.get("item") is None:
        # Nothing currently playing — start playback
        sp.start_playback()
        return
    playing = state.get("is_playing", False)
    if playing:
        sp.pause_playback()
    else:
        sp.start_playback()


def pause(sp):
    sp.pause_playback()


def shuffle_switch(sp, shuffle_button):
    playback = sp.current_playback() or {}
    current_state = playback.get("shuffle_state", False)
    if current_state:
        shuffle_button.config(relief=tk.RAISED, bg="SystemButtonFace", fg="black")
    else:
        shuffle_button.config(relief=tk.SUNKEN, bg="gray40", fg="white")
    sp.shuffle(not current_state)


def search(sp, query):
    results = sp.search(query, type="track")
    tracks = results["tracks"]["items"]

    if len(tracks) == 0:
        print("No tracks found.")
        return

    print("Pick one:")
    for i, track in enumerate(tracks):
        print(f"{i + 1}: {track['name']} by {track['artists'][0]['name']}")

    print("Enter the number of the track you want to play:")
    choice = int(input()) - 1

    track_uri = tracks[choice]["uri"]
    sp.start_playback(uris=[track_uri])


def search_albums(search_box, sp, listbox, album_ids):
    listbox.delete(0, tk.END)
    query = search_box.get()
    results = sp.search(query, type="album")

    resulting_albums = results["albums"]["items"]

    album_ids.clear()

    for i, album in enumerate(resulting_albums):
        if album is not None:
            listbox.insert(
                tk.END, f'{album["name"]} ---- {album["artists"][0]["name"]}')
            album_ids.append(album["id"])


def album_selected(event, sp, album_ids, track_ids, track_listbox, album_id):
    selection = event.widget.curselection()
    if not selection:
        return
    selection_index = selection[0]

    print(
        f"Playlist selected: {event.widget.get(selection_index)}")

    album = sp.album(album_ids[selection_index])
    album_id[0] = album["id"]
    track_ids.clear()
    track_listbox.delete(0, tk.END)
    for track in album["tracks"]["items"]:
        track_listbox.insert(
            tk.END, f"{track['name']} by {track['artists'][0]['name']}")
        track_ids.append(track["uri"])


def track_selected(event, sp, track_ids, album_id, progress_bar):
    if hasattr(progress_bar.track_pb, "after_id"):
        progress_bar.track_pb.after_cancel(
            progress_bar.track_pb.after_id)
    selection = event.widget.curselection()
    if not selection:
        return
    selection_index = selection[0]

    print(
        f"Playing track: {event.widget.get(selection_index)} -- {track_ids[selection_index]}")
    print()
    sp.start_playback(context_uri=f"spotify:album:{album_id[0]}", offset={
        "uri": track_ids[selection_index]
    })


def format_time(ms):
    seconds = ms//1000
    minutes = seconds // 60
    seconds %= 60
    return f"{minutes}:{seconds:02d}"


def mark_toggle(button, state_bool):
    if state_bool:
        button.config(relief=tk.SUNKEN, bg="gray40", fg="white")
    else:
        button.config(relief=tk.RAISED, bg="SystemButtonFace", fg="black")


def update(sp, progress_bar, song_labels, toggles):
    state = get_playback_state(sp)
    if state is None:
        song_labels.name_and_artist.config(text="")
        song_labels.album.config(text="")
        return

    update_song(progress_bar, song_labels, state)
    update_toggles(toggles, state)
    update_album_art(song_labels.album_art, state.album_art)


@dataclass
class State:
    is_playing: bool
    track_name: str
    artist: str
    album: str 
    progress: int 
    duration: int 
    shuffle: bool 
    repeat: bool 
    volume: int 
    album_art: str

def get_playback_state(sp):
    playback = sp.current_playback()

    if playback is None or playback["item"] is None:
        return None

    return State(
        is_playing= playback["is_playing"],
        track_name= playback["item"]["name"],
        artist= playback["item"]["artists"][0]["name"],
        album= playback["item"]["album"]["name"],
        progress= playback["progress_ms"],
        duration= playback["item"]["duration_ms"],
        shuffle= playback["shuffle_state"],
        repeat= playback["repeat_state"],
        volume= playback["device"]["volume_percent"],
        album_art =playback["item"]["album"]["images"][0]["url"] if playback["item"]["album"]["images"] else None
    ) 


def update_song(progress_bar, song_labels, state):

    # UPDATE SONG INFO
    song_name = state.track_name
    artist = state.artist
    song_labels.name_and_artist.config(text=f"{song_name} -- {artist}")
    album = state.album
    song_labels.album.config(text=f"{album}")

    # UPDATE PROGRESS BAR
    duration = state.duration
    progress = state.progress
    progress_bar.track_pb["maximum"] = duration
    progress_bar.track_pb["value"] = progress

    progress_bar.elapsed_label.config(text=format_time(progress))
    progress_bar.duration_label.config(text=format_time(duration))


def update_toggles(toggles, state):
    currently_playing = state.is_playing
    mark_toggle(toggles.play, currently_playing)

    shuffle_state = state.shuffle
    mark_toggle(toggles.shuffle, shuffle_state)


global_album_url = None
global_album_image = None


def update_album_art(album_art_label, album_art_url):
    global global_album_url
    if not album_art_url:
        return
    if global_album_url == album_art_url:
        return
    global_album_url = album_art_url
    print(f"Updating album art with URL: {album_art_url}")
    try:
        response = requests.get(album_art_url, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed fetching album art: {e}")
        return

    try:
        image = Image.open(BytesIO(response.content))
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        album_art_label.config(image=photo)
        global global_album_image
        global_album_image = photo  # Keep a reference to avoid garbage collection
    except Exception as e:
        print(f"Failed processing album art: {e}")
