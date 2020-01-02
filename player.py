import glob

import ffmpeg
import vlc
from urllib.parse import unquote

# files = glob.glob('/disks/transcend/Media/Music/Library/The Wildhearts/P.H.U.Q/*.flac')


class Player(object):
    def __init__(self, current_playlist=None):
        self.initialise_player()
        self.current_index = 0
        self.playing = -1
        self.paused = False
        self.instance = vlc.Instance()
        self.current_track_info = {}
        if current_playlist is None:
            self.playlist = []
        else:
            self.playlist = current_playlist

    def add_to_playlist(self, track):
        self.playlist.append(track)

    def clear_current_track_info(self):
        print('Clearing track info')
        self.current_track_info = {}

    def end_of_song(self, event):
        print('Song Finished')
        self.playing = -1
        self.next()

    def get_info(self):
        player_info = {
            'is_playing': self.player.is_playing(),
        }
        if self.player.is_playing() or self.paused:
            try:
                player_info['track_length'] = int(float(self.current_track_info['duration']) * 1000)
            except KeyError as e:
                print('')
                print('ERROR: {}'.format(e))
                print('')
                print(self.current_track_info)
                print('')
            player_info['track_time'] = self.player.get_time()
            player_info['paused'] = self.paused
        player_info['current_track'] = self.current_index
        return player_info

    def get_playlist(self):
        return self.playlist

    def initialise_player(self):
        self.player = None
        self.player = vlc.MediaPlayer()
        self.player_event_manager = self.player.event_manager()
        self.player_event_manager.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.end_of_song
        )
        self.player_event_manager.event_attach(
            vlc.EventType.MediaPlayerStopped, self.player_stopped
        )
        self.player_event_manager.event_attach(
            vlc.EventType.MediaPlayerPlaying, self.media_playing
        )

    def media_playing(self, event):
        print('Playing: {}'.format(event.u.filename))

    def next(self):
        print('Playing next: {}'.format(self.current_index))
        if self.playing >= 0:
            self.stop()
        if self.current_index == len(self.playlist) - 1:
            self.current_index = 0
        else:
            self.current_index += 1
            print('Next is: {}'.format(self.current_index))
            self.play()

    def pause(self):
        self.player.set_pause(1)
        self.paused = True

    def play(self):
        print('Attempting to play')
        if self.current_index < len(self.playlist):
            media = self.instance.media_new(self.playlist[self.current_index])
            print('Play {}'.format(self.playlist[self.current_index]))
            media.get_mrl()
            self.initialise_player()
            self.player.set_media(media)
            self.player.play()
            self.playing = self.current_index
            self.set_current_track_info()
            self.paused = False

    def play_selected_item(self, index):
        print(self.playlist)
        self.current_index = index
        self.stop()
        self.play()

    def player_stopped(self, event):
        self.playing = -1
        print('Stopped: {}, {}'.format(event.type, event.u))

    def previous(self):
        self.stop()
        if self.current_index == 0:
            self.current_index = len(self.playlist) - 1
        else:
            self.current_index -= 1
            self.play()

    def reload_playlist(self, tracks, reset_index=True):
        self.playlist = [track[4] for track in tracks]
        if reset_index:
            self.current_index = 0

    def remove_from_playlist(self, index):
        print('Playlist {} items'.format(len(self.playlist)))
        del self.playlist[int(index)]
        print('Playlist {} items'.format(len(self.playlist)))

    def resume(self):
        if self.paused:
            self.player.set_pause(0)
            self.paused = False
        else:
            self.play()

    def set_current_track_info(self):
        mrl = self.player.get_media().get_mrl()
        p = ffmpeg.probe(unquote(mrl))
        self.current_track_info = p['format']

    def set_playlist(self, playlist):
        self.playlist = playlist

    def stop(self):
        print('Stopping player')
        self.player.stop()
        self.clear_current_track_info()
        self.paused = False
