"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Last.fm API client

 Signed REST calls to ws.audioscrobbler.com - same shape as
 api/airsonic.py's own auth/request pattern, just Last.fm's
 own MD5 signing scheme instead of Subsonic's salted token.

 Version : 0.1
===========================================================
"""

import hashlib

import requests

import config


API_URL = "https://ws.audioscrobbler.com/2.0/"


class LastfmClient:

    def __init__(self):
        self.api_key = config.LASTFM_API_KEY
        self.api_secret = config.LASTFM_API_SECRET
        self.session_key = config.LASTFM_SESSION_KEY

    def _sign(self, params):
        """
        Last.fm signing: concatenate sorted key+value pairs (excluding
        "format"), append the shared secret, MD5 it.
        """

        ordered = "".join(
            f"{key}{params[key]}"
            for key in sorted(params)
            if key != "format"
        )

        return hashlib.md5((ordered + self.api_secret).encode()).hexdigest()

    def _post(self, method, params):
        payload = {
            "method": method,
            "api_key": self.api_key,
            "sk": self.session_key,
            **params,
        }

        payload["api_sig"] = self._sign(payload)
        payload["format"] = "json"

        response = requests.post(API_URL, data=payload, timeout=config.AIRSONIC_TIMEOUT)
        response.raise_for_status()

        return response.json()

    def update_now_playing(self, artist, title, album=None, duration=None):
        params = {"artist": artist, "track": title}

        if album:
            params["album"] = album

        if duration:
            params["duration"] = int(duration)

        return self._post("track.updateNowPlaying", params)

    def scrobble(self, artist, title, timestamp, album=None, duration=None):
        params = {"artist": artist, "track": title, "timestamp": int(timestamp)}

        if album:
            params["album"] = album

        if duration:
            params["duration"] = int(duration)

        return self._post("track.scrobble", params)


client = LastfmClient()
