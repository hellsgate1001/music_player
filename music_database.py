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

    def add_track_to_current_playlist(self, track_id):
        playlist = self.get_playlist()
        try:
            track_ids = playlist[1].split(',')
        except AttributeError:
            track_ids = []
        track_ids.append(track_id)
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            update = "UPDATE playlist SET tracks = ? WHERE rowid = ?"
            cur.execute(update, (','.join(str(t) for t in track_ids), playlist[2]))
            conn.commit()

    def add_multiple_to_current_playlist(self, track_ids):
        print('Adding {} to playlist'.format(track_ids))
        playlist = self.get_playlist()
        try:
            current_ids = all(playlist[1].split(',')) or []
        except AttributeError:
            current_ids = []
        current_ids.extend(track_ids)
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            update = "UPDATE playlist SET tracks = ? WHERE rowid = ?"
            cur.execute(update, (','.join(str(t) for t in current_ids), playlist[2]))
            conn.commit()

    def build_playlist(self, rows, tracks):
        # Playlist doesn't always come back from the database in the order of the tracks listed. Ensure
        # the order is retained
        playlist = []
        for track in tracks:
            for row in rows:
                if row[5] == int(track):
                    playlist.append(row)
                    break
        return playlist

    def clear_playlist(self):
        current_playlist = self.get_current_playlist()
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            clear = 'UPDATE playlist SET tracks = "" WHERE rowid = ?'
            cur.execute(clear, (current_playlist,))
            conn.commit()
        return True

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

    def get_artists_by_filter(self, filter_text):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT DISTINCT(artist) FROM music WHERE artist LIKE ? ORDER BY artist'
            cur.execute(select, ('%{}%'.format(filter_text),))
            rows = cur.fetchall()
        return rows

    def get_albums_by_filter(self, filter_text):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT DISTINCT artist, album FROM music WHERE album LIKE ? ORDER BY artist, album'
            cur.execute(select, ('%{}%'.format(filter_text),))
            rows = cur.fetchall()
        return rows

    def get_albums_for_artist(self, artist):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT DISTINCT album FROM music WHERE artist = ? ORDER BY album'
            cur.execute(select, (artist,))
            rows = cur.fetchall()
        return rows

    def get_tracks_by_filter(self, filter_text):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT DISTINCT artist, album, title FROM music WHERE title LIKE ? ORDER BY artist, album, track_number'
            cur.execute(select, ('%{}%'.format(filter_text),))
            rows = cur.fetchall()
        return rows

    def get_tracks_for_album(self, artist, album):
        print('Getting tracks for album: {} - {}'.format(album, artist))
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT *, rowid FROM music WHERE artist = ? AND album = ? ORDER BY track_number'
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
            select = 'SELECT *, rowid FROM music ORDER BY artist, album, track_number'
            cur.execute(select)
            rows = cur.fetchall()
        return rows

    def get_track(self, artist, album, tracknum):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT *, rowid FROM music WHERE artist = ? AND album = ? AND track_number = ?'
            cur.execute(select, (artist, album, tracknum))
            row = cur.fetchone()
        return row

    def get_playlist(self):
        current_playlist = self.get_current_playlist()
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT *, rowid FROM playlist WHERE rowid = ?'
            cur.execute(select, '{}'.format(current_playlist))
            row = cur.fetchone()
        return row

    def get_playlist_tracks(self):
        playlist = self.get_playlist()
        tracks = playlist[1].split(',')
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            track_select = 'SELECT *, rowid FROM music WHERE rowid in ({})'.format(','.join(['?'] * len(tracks)))
            cur.execute(track_select, tracks)
            rows = cur.fetchall()
        return self.build_playlist(rows, tracks)

    def get_current_playlist(self):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT current_playlist FROM current_playlist WHERE rowid = 1'
            cur.execute(select)
            row = cur.fetchone()
        return row[0]

    def get_current_index(self):
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT current_index FROM current_index WHERE rowid = 1'
            cur.execute(select)
            row = cur.fetchone()
        return row

    def load_playlist(self):
        current_playlist = self.get_current_playlist()
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            select = 'SELECT * FROM playlist WHERE rowid = ?'
            cur.execute(select, (current_playlist,))
            row = cur.fetchone()
        return row[1].split(',')

    def remove_track_from_playlist(self, track_index):
        playlist = self.get_playlist()
        tracks = playlist[1].split(',')
        del tracks[int(track_index)]
        with sq.connect(self.db_file) as conn:
            cur = conn.cursor()
            update = 'UPDATE playlist SET tracks = ? WHERE rowid = ?'
            cur.execute(update, (','.join(tracks), playlist[2]))
            conn.commit()
        return True

    def close_connection(self):
        self.conn.close()
