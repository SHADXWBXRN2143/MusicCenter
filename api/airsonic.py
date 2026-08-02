"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Airsonic / Subsonic API client

 Version : 0.2
===========================================================
"""

import hashlib
import random
import string
from urllib.parse import urlencode

import requests

import config


class AirsonicClient:
    """
    Airsonic / Subsonic API client
    """

    def __init__(self):
        self.base_url = config.AIRSONIC_URL.rstrip("/")
        self.username = config.AIRSONIC_USERNAME
        self.password = config.AIRSONIC_PASSWORD

        self.client_name = config.AIRSONIC_CLIENT_NAME
        self.version = config.AIRSONIC_API_VERSION

        self.timeout = config.AIRSONIC_TIMEOUT

    def _auth(self):
        """
        Airsonic token authentication
        """

        salt = "".join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(16)
        )

        token = hashlib.md5(
            (self.password + salt).encode()
        ).hexdigest()

        return {
            "u": self.username,
            "t": token,
            "s": salt,
            "v": self.version,
            "c": self.client_name,
            "f": "json"
        }

    def _request(self, endpoint, params=None):
        """
        Universal JSON API request
        """

        try:
            query = self._auth()

            if params:
                query.update(params)

            url = f"{self.base_url}/rest/{endpoint}"

            response = requests.get(url, params=query, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            return data.get("subsonic-response", {})

        except Exception as e:
            print(f"Airsonic API error {endpoint}: {e}")
            return {}

    def _raw_request(self, endpoint, params=None):
        """
        Raw binary request (cover art, streams)
        """

        query = self._auth()
        query.pop("f", None)

        if params:
            query.update(params)

        url = f"{self.base_url}/rest/{endpoint}"

        response = requests.get(url, params=query, timeout=self.timeout)
        response.raise_for_status()

        return response.content

    def _signed_url(self, endpoint, params=None):
        """
        Build a fully authenticated URL for external players (mpv)
        """

        query = self._auth()
        query.pop("f", None)

        if params:
            query.update(params)

        return f"{self.base_url}/rest/{endpoint}?{urlencode(query)}"

    # ==========================
    # SYSTEM
    # ==========================

    def ping(self):
        return self._request("ping.view")

    # ==========================
    # ARTISTS
    # ==========================

    def get_artists(self):
        data = self._request("getArtists.view")

        groups = data.get("artists", {}).get("index", [])

        result = []

        for group in groups:
            for artist in group.get("artist", []):
                result.append(artist)

        return result

    def get_artist(self, artist_id):
        data = self._request("getArtist.view", {"id": artist_id})
        return data.get("artist", {})

    # ==========================
    # ALBUMS
    # ==========================

    def get_album_list(self, limit=100):
        data = self._request(
            "getAlbumList2.view",
            {"type": "newest", "size": limit}
        )

        return data.get("albumList2", {}).get("album", [])

    def get_album(self, album_id):
        data = self._request("getAlbum.view", {"id": album_id})
        return data.get("album", {})

    # ==========================
    # SONGS
    # ==========================

    def get_random_songs(self, limit=50):
        data = self._request("getRandomSongs.view", {"size": limit})
        return data.get("randomSongs", {}).get("song", [])

    def get_song(self, song_id):
        data = self._request("getSong.view", {"id": song_id})
        return data.get("song", {})

    # ==========================
    # SEARCH
    # ==========================

    def search(self, query):
        data = self._request(
            "search3.view",
            {"query": query, "artistCount": 20, "albumCount": 20, "songCount": 30}
        )

        result3 = data.get("searchResult3", {})

        return {
            "artist": result3.get("artist", []),
            "album": result3.get("album", []),
            "song": result3.get("song", []),
        }

    # ==========================
    # ARTWORK / STREAM
    # ==========================

    def get_cover_art(self, cover_id, size=None):
        params = {"id": cover_id}

        if size:
            params["size"] = size

        return self._raw_request("getCoverArt.view", params)

    def stream_url(self, track_id):
        return self._signed_url("stream.view", {"id": track_id})


client = AirsonicClient()
