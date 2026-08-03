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

    # ==========================
    # SIMILAR / RADIO
    # ==========================

    def get_similar(self, artist_id, limit=20):
        try:
            songs = []

            if artist_id:
                songs = self.client.get_similar_songs(artist_id, count=limit)

            if not songs:
                songs = self.client.get_random_songs(limit=limit)

            return [_with_stream(song) for song in songs]
        except Exception as e:
            print("Similar songs error:", e)
            return []

    # ==========================
    # FAVORITES
    # ==========================

    def get_favorites(self):
        try:
            starred = self.client.get_starred()

            return {
                "artists": starred.get("artist", []),
                "albums": starred.get("album", []),
                "songs": [_with_stream(song) for song in starred.get("song", [])],
            }
        except Exception as e:
            print("Favorites error:", e)
            return {"artists": [], "albums": [], "songs": []}

    def star(self, item_id, kind="song"):
        try:
            self.client.star(item_id, kind=kind)
            return True
        except Exception as e:
            print("Star error:", e)
            return False

    def unstar(self, item_id, kind="song"):
        try:
            self.client.unstar(item_id, kind=kind)
            return True
        except Exception as e:
            print("Unstar error:", e)
            return False

    # ==========================
    # PLAYLISTS
    # ==========================

    def get_playlists(self):
        try:
            return self.client.get_playlists()
        except Exception as e:
            print("Playlists error:", e)
            return []

    def get_playlist(self, playlist_id):
        try:
            playlist = self.client.get_playlist(playlist_id)

            if not playlist:
                return {}

            playlist = dict(playlist)
            entries = playlist.get("entry", playlist.get("song", []))
            playlist["tracks"] = [_with_stream(song) for song in entries]

            return playlist
        except Exception as e:
            print("Playlist error:", e)
            return {}

    def create_playlist(self, name, song_ids=None):
        try:
            return self.client.create_playlist(name, song_ids=song_ids)
        except Exception as e:
            print("Create playlist error:", e)
            return {}

    def add_to_playlist(self, playlist_id, song_id):
        try:
            self.client.update_playlist(playlist_id, add_song_id=song_id)
            return True
        except Exception as e:
            print("Add to playlist error:", e)
            return False

    def remove_from_playlist(self, playlist_id, index):
        try:
            self.client.update_playlist(playlist_id, remove_index=index)
            return True
        except Exception as e:
            print("Remove from playlist error:", e)
            return False

    def delete_playlist(self, playlist_id):
        try:
            self.client.delete_playlist(playlist_id)
            return True
        except Exception as e:
            print("Delete playlist error:", e)
            return False


service = AirsonicService()
