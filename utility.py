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


def shuffle_switch(sp):
    current_state = sp.current_playback()["shuffle_state"]
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
    # print(results)
    # return
    resulting_albums = results["albums"]["items"]
    # print(resulting_albums)
    
    # clear previous search results
    album_ids.clear()

    for i, album in enumerate(resulting_albums):
        if album is not None:
            listbox.insert(
                tk.END, f'{album["name"]} ---- {album["artists"][0]["name"]}')
            album_ids.append(album["id"])

def album_selected(event, sp, album_ids, track_ids, track_listbox):
    print(
        f"Playlist selected: {event.widget.get(event.widget.curselection())}")
    selection_index = event.widget.curselection()[0]
    # sp.start_playback(
    #     context_uri=f"spotify:album:{album_ids[selection_index]}")

    album = sp.album(album_ids[selection_index])
    track_ids.clear()
    track_listbox.delete(0, tk.END)
    for track in album["tracks"]["items"]:
        track_listbox.insert(
            tk.END, f"{track['name']} by {track['artists'][0]['name']}")
        track_ids.append(track["uri"])


def track_selected(event, sp, album_ids, track_ids):
    # print("hello")
    print(f"Track selected: {event.widget.get(event.widget.curselection())}")
    selection_index = event.widget.curselection()[0]





    print(f"Playing track: {event.widget.get(selection_index)} -- {track_ids[selection_index]}")
    # sp.start_playback(uris=[track_ids[selection_index]])
    # playback = sp.current_user_playing_track()

    # Check if a track is playing and if it belongs to a context
    # if playback and playback.get('context'):
    #     context_type = playback['context']['type']

    #     # Verify the context is a playlist (not an album or artist)
    #     if context_type == 'playlist':
    #         playlist_uri = playback['context']['uri']
    #         return playlist_uri
    #     else:
    #         return f"The current context is an {context_type}, not a playlist."

    # return "No active playlist context found (e.g., listening to Liked Songs or radio)."

def track_selected(event, sp, album_ids, track_ids, album_listbox=None):
    sel = event.widget.curselection()
    if not sel:
        return
    selection_index = sel[0]

    print(f"Track selected: {event.widget.get(selection_index)}")
    print(f"Playing track: {event.widget.get(selection_index)} -- {track_ids[selection_index]}")

    # Determine the album context index. Prefer the passed-in album_listbox selection
    album_index = None
    if album_listbox:
        a_sel = album_listbox.curselection()
        if a_sel:
            album_index = a_sel[0]

    # If no album index found, fall back to using the track index (best-effort)
    if album_index is None:
        album_index = selection_index

    # Try playing within album context; fall back to direct URI play if it fails
    try:
        sp.start_playback(context_uri=f"spotify:album:{album_ids[album_index]}", offset={
            "uri": track_ids[selection_index]
        })
    except Exception:
        sp.start_playback(uris=[track_ids[selection_index]])
