import tkinter as tk


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
    sp.start_playback()


def pause(sp):
    sp.pause_playback()


def shuffle_switch(sp, shuffle_button):
    current_state = sp.current_playback()["shuffle_state"]
    if current_state:
        shuffle_button.config(
            text="Shuffle Off", relief=tk.RAISED, bg="SystemButtonFace", fg="black")
    else:
        shuffle_button.config(
            text="Shuffle On", relief=tk.SUNKEN, bg="gray40", fg="white")
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


def track_selected(event, sp, track_ids, album_id, track_pb):

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
    track_pb["value"] = 0
    current = sp.current_user_playing_track()
    song_length = current["item"]["duration_ms"]
    step = song_length/100
    track_pb.start(int(step))