import sqlite3 as sq


class MusicDatabase(object):
    def __init__(self, db_file):
        self.db_file = db_file

    def create_connection(self, db_file):
        try:
            self.conn = sq.connect(db_file)
            self.cur = self.conn.cursor()
        except Exception as e:
            print(e)

    def get_artists(self):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT DISTINCT artist FROM music ORDER BY artist'
            cur.execute(select)
            rows = cur.fetchall()
        return rows

    def get_artist(self, artist):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT * FROM music WHERE artist = ? ORDER BY album, track_number'
            cur.execute(select, (artist,))
            rows = cur.fetchall()
        return rows

    def get_albums_for_artist(self, artist):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT DISTINCT album FROM music WHERE artist = ? ORDER BY album'
            cur.execute(select, (artist,))
            rows = cur.fetchall()
        return rows

    def get_tracks_for_album(self, artist, album):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT * FROM music WHERE artist = ? AND album = ? ORDER BY track_number'
            cur.execute(select, (artist, album))
            rows = cur.fetchall()
        return rows

    def get_album(self, album):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT * FROM music WHERE album = ? ORDER BY track_number'
            cur.execute(select, (album,))
            rows = cur.fetchall()
        return rows

    def get_all(self):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT * FROM music ORDER BY artist, album, track_number'
            cur.execute(select)
            rows = cur.fetchall()
        return rows

    def get_song(self, artist, album, tracknum):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT * FROM music WHERE artist = ? AND album = ? AND track_number = ?'
            cur.execute(select, (artist, album, tracknum))
            row = cur.fetchone()
        return row


    def close_connection(self):
        self.conn.close()
