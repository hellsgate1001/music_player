import glob

import vlc

# files = glob.glob('/disks/transcend/Media/Music/Library/The Wildhearts/P.H.U.Q/*.flac')
files =[]
playlist = []
player = vlc.MediaPlayer()
medialist = vlc.MediaList(files)
mlplayer = vlc.MediaListPlayer()
mlplayer.set_media_player(player)
mlplayer.set_media_list(medialist)


def add_to_list(media):
    medialist.lock()
    medialist.add_media(media)
    medialist.unlock()


def get_playlist():
    return


def next():
    mlplayer.next()


def pause():
    mlplayer.pause()


def play():
    mlplayer.play()


def play_selected_item(index):
    mlplayer.play_item_at_index(index)


def previous():
    mlplayer.previous()


def reload_playlist():
    files = [track[4] for track in playlist]
    mlplayer.stop()
    medialist = vlc.MediaList(files)
    mlplayer.set_media_list(medialist)


def remove_from_list(track):
    # medialist.lock()
    # medialist.remove_index(index)
    # medialist.unlock()
    playlist.remove(track)


def stop():
    mlplayer.stop()
