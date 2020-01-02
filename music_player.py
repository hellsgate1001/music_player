import eventlet
eventlet.monkey_patch()
import json
import time
import os
from pathlib import Path

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from info_api import get_album_info
from music_database import MusicDatabase
from player import Player

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
mdb = MusicDatabase(os.path.join(os.getcwd(), 'music.sqlite3'))
current_playlist = mdb.get_playlist_tracks()
player = Player([track[4] for track in current_playlist])
worker = None


class Worker(object):
    switch = False
    unit_of_work = 0

    def __init__(self, socketio):
        self.socketio = socketio
        self.switch = True

    def do_work(self):
        while self.switch:
            self.socketio.emit('get_info', player.get_info(), namespace='/')
            eventlet.sleep(0.5)

    def stop(self):
        self.switch = False


@app.route('/add-album-to-playlist/<artist>/<album>')
def add_album_to_playlist(artist, album):
    tracks = mdb.get_tracks_for_album(artist, album)
    track_ids = [track[5] for track in tracks]
    mdb.add_multiple_to_current_playlist(track_ids)
    player.set_playlist([track[4] for track in tracks])
    return get_playlist()


@app.route('/add-to-playlist/<artist>/<album>/<tracknum>')
def add_to_playlist(artist, album, tracknum):
    track = mdb.get_track(artist, album, tracknum)
    mdb.add_track_to_current_playlist(track[5])
    player.add_to_playlist(track[4])
    return get_playlist()


@app.route('/artists')
def get_artists():
    print('Getting Artists')
    all_artists = mdb.get_artists()
    artists = [artist[0] for artist in all_artists]
    return json.dumps(artists)


@app.route('/artist/<artist>')
def get_albums_for_artist(artist):
    artist_albums = mdb.get_albums_for_artist(artist)
    return json.dumps([album[0] for album in artist_albums])


@app.route('/get-playlist')
def get_playlist():
    playlist_tracks = mdb.get_playlist_tracks()
    return json.dumps(playlist_tracks)


@app.route('/artist/<artist>/<album>')
def get_tracks_for_album(artist, album):
    tracks = mdb.get_tracks_for_album(artist, album)
    return json.dumps([track[:4] for track in tracks])


@app.route('/filter/<filter_text>')
def filter(filter_text):
    filtered_artists = mdb.get_artists_by_filter(filter_text)
    filtered_albums = mdb.get_albums_by_filter(filter_text)
    filtered_tracks = mdb.get_tracks_by_filter(filter_text)
    response = {
        'artists': filtered_artists,
        'albums': filtered_albums,
        'tracks': filtered_tracks,
    }
    return json.dumps(response)


@app.route('/pause')
def pause():
    player.pause()
    return ('', 204)


@app.route('/play-album/<artist>/<album>')
def play_album(artist, album):
    global worker
    tracks = mdb.get_tracks_for_album(artist, album)
    player.reload_playlist(tracks)
    player.play()
    if worker is None:
        worker = Worker(socketio)
        socketio.start_background_task(target=worker.do_work)
    return ('', 204)


@app.route('/play-from-list/<index>')
def play_from_list(index):
    global worker
    player.play_selected_item(int(index))
    if worker is None:
        worker = Worker(socketio)
        socketio.start_background_task(target=worker.do_work)
    return ('', 204)


@app.route('/remove-from-playlist/<index>')
def remove_from_playlist(index):
    mdb.remove_track_from_playlist(index)
    player.remove_from_playlist(index)
    return get_playlist()


@app.route('/resume')
def resume():
    global worker
    player.resume()
    if worker is None:
        worker = Worker(socketio)
        socketio.start_background_task(target=worker.do_work)
    return ('', 204)


@app.route('/re-order-list', methods=['POST'])
def re_order_list():
    new_list = request.get_json()
    track_ids = [track[5] for track in new_list]
    mdb.clear_playlist()
    mdb.add_multiple_to_current_playlist(track_ids)
    playlist_tracks = mdb.get_playlist_tracks()
    return json.dumps(playlist_tracks)


@app.route('/stop')
def stop():
    global worker
    player.stop()
    worker.stop()
    worker = None
    return ('', 204)


@app.route('/get-currently-playing')
def get_currently_playing():
    return json.dumps({'current_track_index': player.current_index})


@app.route('/get-player-info')
def get_player_info():
    return json.dumps(player.get_info())

@app.route('/create-image/<artist>/<album>')
def create_image(artist, album):
    image_name = '{artist} - {album}.jpg'.format(
        artist=artist.lower(), album=album.lower()
    )
    album_image = Path('static/images/{}'.format(image_name))
    if not album_image.is_file():
        get_album_info(artist, album)
    return json.dumps({'image_exists': album_image.is_file()})


@socketio.on('reorder')
def on_reorder():
    print('Emitting list reordering')
    playlist_tracks = mdb.get_playlist_tracks()
    socketio.emit('list_reordered', playlist_tracks)


@socketio.on('get_info')
def on_get_info(data):
    print('Getting player info')
    player_info = player.get_info()
    print('Received {}'.format(data))
    emit('get_info', player_info)


@socketio.on('connect')
def on_connect():
    print('CONNECTED')
    emit('connect', {'connected': True})


@socketio.on('message')
def on_message():
    print('Received Message')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
