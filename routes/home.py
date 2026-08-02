"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Home Routes

 Version : 0.2
===========================================================
"""

from flask import Blueprint, render_template

import config
from services.airsonic_service import service


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():

    albums = service.get_albums(limit=config.RECENT_ALBUM_COUNT)
    artists = service.get_artists()[:config.RECENT_ARTIST_COUNT]

    tracks = []

    for album in albums[:5]:
        full_album = service.get_album(album["id"])

        for track in full_album.get("tracks", []):
            tracks.append(track)

            if len(tracks) >= config.RECENT_TRACK_COUNT:
                break

        if len(tracks) >= config.RECENT_TRACK_COUNT:
            break

    return render_template(
        "index.html",
        page_title="Главная",
        active_page="home",
        albums=albums,
        artists=artists,
        tracks=tracks,
    )
