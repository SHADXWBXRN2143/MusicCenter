"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Artist Routes

 Version : 0.3
===========================================================
"""

from flask import Blueprint, render_template, request

from services.airsonic_service import service


artists_bp = Blueprint("artists", __name__)

SORT_OPTIONS = {
    "name": "По алфавиту",
    "albumCount": "По числу альбомов",
}


@artists_bp.route("/")
def artists():

    sort = request.args.get("sort", "name")

    if sort not in SORT_OPTIONS:
        sort = "name"

    artists = service.get_artists(sort=sort)

    return render_template(
        "artists.html",
        page_title="Исполнители",
        active_page="artists",
        artists=artists,
        sort=sort,
        sort_options=SORT_OPTIONS,
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
