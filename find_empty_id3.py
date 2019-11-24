import os

from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import HeaderNotFoundError

from util import get_files_of_type, load_mp3, KEYS

'''
mp3 tags
TSSE: LAME v3.97
TIT2: Circle
TPE1: Slipknot
TALB: Vol. 3: The Subliminal Verses
COMM::XXX: EAC.LAMEv3.97-V2
TRCK: 6
TCON: Metal
COMM:ID3v1 Comment:eng: EAC.LAMEv3.97-V2
TDRC: 2004
'''

previous = {
    'artist': '',
    'album': ''
}
previous_path = ''


def mp3_has_missing_info(mp3):
    try:
        values = [mp3[k][0] for k in KEYS]
        return '' in values
    except KeyError:
        return True


def flac_has_missing_info(flac):
    try:
        values = [flac[k][0] for k in KEYS]
        return '' in values
    except KeyError:
        return True


def update_mp3_id3(mp3_path):
    global previous
    global previous_path
    mp3 = EasyID3(mp3_path)
    print(mp3_path)
    save = False
    for key in KEYS:
        try:
            print('{}: {}'.format(key, mp3[key][0] or ''))
        except KeyError:
            if (key in previous.keys() and previous[key] != '' and
                    previous_path == os.path.dirname(mp3_path)):
                prompt = '{} ({}):'.format(key, previous[key])
            else:
                prompt = '{}:'.format(key)
            print(prompt)
            value = input('Enter value: ')
            if (key in previous.keys() and previous[key] != '' and
                    value == '' and previous_path == os.path.dirname(mp3_path)):
                mp3[key] = previous[key]
            else:
                mp3[key] = value
            if key in previous.keys() and value != '':
                previous[key] = value
            save = True
    previous_path = os.path.dirname(mp3_path)
    if save:
        mp3.save()


def update_flac_id3(flac_path):
    global previous
    global previous_path
    flac = FLAC(flac_path)
    print(flac_path)
    save = False
    for key in KEYS:
        try:
            print('{}: {}'.format(key, flac[key][0] or ''))
        except KeyError:
            if (key in previous.keys() and previous[key] != '' and
                    previous_path == os.path.dirname(flac_path)):
                prompt = '{} ({})'.format(key, previous[key])
            else:
                prompt = '{}'.format(key)
            print(prompt)
            value = input('Enter value: ')
            if (key in previous.keys() and previous[key] != '' and
                    value == '' and previous_path == os.path.dirname(flac_path)):
                flac[key] = previous[key]
            else:
                flac[key] = value
            if key in previous.keys() and value != '':
                previous[key] = value
            save = True
    previous_path = os.path.dirname(flac_path)
    if save:
        flac.save()


def main():
    mp3s = get_files_of_type('mp3')
    flacs = get_files_of_type('flac')

    missing_mp3s = [mp3 for mp3 in mp3s if mp3_has_missing_info(load_mp3(mp3))]
    missing_flacs = [
        flac for flac in flacs if flac_has_missing_info(FLAC(flac))
    ]

    print('{} mp3s, {} flacs'.format(len(missing_mp3s), len(missing_flacs)))
    print('{} mp3s, {} flacs'.format(missing_mp3s, missing_flacs))

    for mp3_path in missing_mp3s:
        update_mp3_id3(mp3_path)

    for flac_path in missing_flacs:
        update_flac_id3(flac_path)

    print('Done!!')


if __name__ == '__main__':
    main()
