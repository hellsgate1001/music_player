import argparse
import os
import sqlite3 as sq

from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC

from util import get_files_of_type, KEYS


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sq.connect(db_file)
        return conn
    except Exception as e:
        print(e)

    return conn


def insert_mp3s(mp3_paths, cur, conn):
    for mp3_path in mp3_paths:
        mp3 = EasyID3(mp3_path)
        insert_values(mp3, mp3_path, cur)
    conn.commit()


def insert_flacs(flacs, cur, conn):
    for flac_path in flacs:
        flac = FLAC(flac_path)
        insert_values(flac, flac_path, cur)
    conn.commit()


def insert_values(music_obj, file_path, cur):
    try:
        track_number = int(music_obj['tracknumber'][0])
    except ValueError:
        print('Updating tracknum for {}'.format(file_path))
        tracknum = music_obj['tracknumber'][0]
        track_number = int(tracknum[:tracknum.index('/')])
        music_obj['tracknumber'] = '{}'.format(track_number)
        music_obj.save()
    try:
        file_values = [
            music_obj['artist'][0],
            music_obj['album'][0],
            music_obj['title'][0],
            track_number,
            file_path
        ]
        insert = '''INSERT INTO music
        (artist, album, title, track_number, path)
        VALUES
        (?, ?, ?, ?, ?)'''
        cur.execute(insert, file_values)
        print(
            'Inserted {} - {} - {} ({})'.format(
                music_obj['artist'][0],
                music_obj['album'][0],
                music_obj['title'][0],
                track_number
            )
        )
    except sq.IntegrityError as e:
        import pdb;pdb.set_trace()
    except Exception as e:
        print(
            'Error inserting {}'.format(file_path)
        )
        print('Error: {}'.format(e))
        raise e


def main(path):
    # Create the database connection
    conn = create_connection(os.path.join(os.getcwd(), 'music.sqlite3'))
    cur = conn.cursor()

    # Get the list of MP3 files
    mp3s = get_files_of_type('mp3', path)
    # Get the list of FLAC files
    flacs = get_files_of_type('flac', path)

    # Insert the MP3s
    insert_mp3s(mp3s, cur, conn)

    # Insert the FLACs
    insert_flacs(flacs, cur, conn)

    # Close the database connection
    conn.close()

    # All done!
    print('Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help='Path to glob for .mp3 and .flac files', dest='path')
    args = parser.parse_args()

    main(args.path)
