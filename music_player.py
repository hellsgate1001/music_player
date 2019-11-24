import json
import os

from flask import Flask
from flask_cors import CORS

import player
from music_database import MusicDatabase

app = Flask(__name__)
CORS(app)
mdb = MusicDatabase(os.path.join(os.getcwd(), 'music.sqlite3'))


@app.route('/add-album-to-playlist/<artist>/<album>')
def add_album_to_playlist(artist, album):
    songs = mdb.get_tracks_for_album(artist, album)
    player.playlist.extend(songs)
    return ('', 204)


@app.route('/add-to-playlist/<artist>/<album>/<tracknum>')
def add_to_playlist(artist, album, tracknum):
    song = mdb.get_song(artist, album, tracknum)
    player.add_to_list(song[4])
    return ('', 204)


@app.route('/artists')
def get_artists():
    all_artists = mdb.get_artists()
    artists = [artist[0] for artist in all_artists]
    return json.dumps(artists)


@app.route('/artist/<artist>')
def get_albums_for_artist(artist):
    artist_albums = mdb.get_albums_for_artist(artist)
    return json.dumps([album[0] for album in artist_albums])


@app.route('/get-playlist')
def get_playlist():
    return json.dumps(player.playlist)


@app.route('/artist/<artist>/<album>')
def get_tracks_for_album(artist, album):
    tracks = mdb.get_tracks_for_album(artist, album)
    return json.dumps([track[:4] for track in tracks])


@app.route('/play-album/<artist>/<album>')
def play_album(artist, album):
    songs = mdb.get_tracks_for_album(artist, album)
    player.playlist = songs
    player.reload_playlist()
    player.play()
    return ('', 204)


@app.route('/play-from-list/<artist>/<album>/<tracknum>')
def play_from_list(artist, album, tracknum):
    selected_track = mdb.get_song(artist, album, tracknum)
    list_index = player.playlist.index(selected_track)
    player.play_selected_item(list_index)
    return ('', 204)


@app.route('/remove-from-playlist/<artist>/<album>/<tracknum>')
def remove_from_playlist(artist, album, tracknum):
    track = mdb.get_song(artist, album, tracknum)
    player.remove_from_list(track)
    return get_playlist()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
