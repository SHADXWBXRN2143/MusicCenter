"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Artist Routes

 Version : 0.2
===========================================================
"""

from flask import Blueprint, render_template

from services.airsonic_service import service


artists_bp = Blueprint("artists", __name__)


@artists_bp.route("/")
def artists():

    artists = service.get_artists()

    return render_template(
        "artists.html",
        page_title="Исполнители",
        active_page="artists",
        artists=artists,
    )


@artists_bp.route("/<artist_id>")
def artist_detail(artist_id):

    artist = service.get_artist(artist_id)

    return render_template(
        "artist.html",
        page_title=artist.get("name", "Исполнитель"),
        active_page="artists",
        artist=artist,
    )
