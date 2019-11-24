import glob

from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

KEYS = ['artist', 'title', 'album', 'tracknumber']


def create_mp3_meta(mp3_path):
    meta = File(mp3_path, easy=True)
    meta.add_tags()
    meta.save(mp3_path)


def get_files_of_type(filetype, path='/disks/transcend/Media/Music/Library'):
    return glob.glob(
        '{}/**/*.{}'.format(path, filetype),
        recursive=True
    )


def load_mp3(mp3_path):
    try:
        mp3 = EasyID3(mp3_path)
    except ID3NoHeaderError:
        create_mp3_meta(mp3_path)
        mp3 = EasyID3(mp3_path)

    return mp3
