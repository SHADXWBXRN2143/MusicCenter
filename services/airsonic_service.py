"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Airsonic Service

 Normalizes raw Subsonic API responses into the shapes
 the routes/templates/frontend expect.

 Version : 0.2
===========================================================
"""

from api.airsonic import client


def _with_stream(song):
    song = dict(song)
    song["stream"] = client.stream_url(song["id"])
    return song


class AirsonicService:

    def __init__(self):
        self.client = client

    # ==========================
    # STATISTICS
    # ==========================

    def get_statistics(self):
        return {
            "artists": len(self.get_artists()),
            "albums": len(self.get_albums(limit=200)),
            "songs": len(self.get_songs()),
        }

    # ==========================
    # ARTISTS
    # ==========================

    def get_artists(self):
        try:
            return self.client.get_artists()
        except Exception as e:
            print("Artists error:", e)
            return []

    def get_artist(self, artist_id):
        try:
            artist = self.client.get_artist(artist_id)

            if not artist:
                return {}

            artist = dict(artist)
            artist["albums"] = artist.get("album", [])

            return artist
        except Exception as e:
            print("Artist error:", e)
            return {}

    # ==========================
    # ALBUMS
    # ==========================

    def get_albums(self, limit=20):
        try:
            return self.client.get_album_list(limit=limit)
        except Exception as e:
            print("Albums error:", e)
            return []

    def get_album(self, album_id):
        try:
            album = self.client.get_album(album_id)

            if not album:
                return {}

            album = dict(album)
            album["tracks"] = [
                _with_stream(song)
                for song in album.get("song", [])
            ]

            return album
        except Exception as e:
            print("Album error:", e)
            return {}

    def recently_added(self, limit=10):
        return self.get_albums(limit=limit)

    # ==========================
    # SONGS
    # ==========================

    def get_songs(self, limit=20):
        try:
            songs = self.client.get_random_songs(limit=limit)
            return [_with_stream(song) for song in songs]
        except Exception as e:
            print("Songs error:", e)
            return []

    def get_song(self, song_id):
        try:
            song = self.client.get_song(song_id)

            if not song:
                return {}

            return _with_stream(song)
        except Exception as e:
            print("Song error:", e)
            return {}

    # ==========================
    # SEARCH
    # ==========================

    def search(self, query):
        try:
            results = self.client.search(query)

            return {
                "artists": results.get("artist", []),
                "albums": results.get("album", []),
                "songs": [_with_stream(song) for song in results.get("song", [])],
            }
        except Exception as e:
            print("Search error:", e)
            return {"artists": [], "albums": [], "songs": []}


service = AirsonicService()
