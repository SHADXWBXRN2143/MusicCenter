"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Last.fm Service

 Passive scrobbling wrapper around api/lastfm.py - no-ops
 quietly when no session key is configured, same degrade-
 gracefully approach as the rest of the services/ layer.

 Version : 0.1
===========================================================
"""

import config

from api.lastfm import client


class LastfmService:

    def __init__(self):
        self.client = client
        self.available = bool(config.LASTFM_SESSION_KEY)

    def update_now_playing(self, track):
        if not self.available:
            return

        try:
            self.client.update_now_playing(
                artist=track.get("artist", ""),
                title=track.get("title", ""),
                album=track.get("album"),
                duration=track.get("duration"),
            )
        except Exception as e:
            print("Last.fm now playing error:", e)

    def scrobble(self, track, timestamp):
        if not self.available:
            return

        try:
            self.client.scrobble(
                artist=track.get("artist", ""),
                title=track.get("title", ""),
                timestamp=timestamp,
                album=track.get("album"),
                duration=track.get("duration"),
            )
        except Exception as e:
            print("Last.fm scrobble error:", e)


lastfm = LastfmService()
