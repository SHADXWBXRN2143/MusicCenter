"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Album Routes

 Version : 0.3
===========================================================
"""

from flask import Blueprint, render_template, request

from services.airsonic_service import service


albums_bp = Blueprint("albums", __name__)

SORT_OPTIONS = {
    "newest": "Новые",
    "alphabeticalByName": "По алфавиту",
    "alphabeticalByArtist": "По исполнителю",
    "byYear": "По году",
    "random": "Случайно",
}


@albums_bp.route("/")
def albums():

    sort = request.args.get("sort", "newest")

    if sort not in SORT_OPTIONS:
        sort = "newest"

    albums = service.get_albums(limit=200, sort=sort)

    return render_template(
        "albums.html",
        page_title="Альбомы",
        active_page="albums",
        albums=albums,
        sort=sort,
        sort_options=SORT_OPTIONS,
    )


@albums_bp.route("/<album_id>")
def album_detail(album_id):

    album = service.get_album(album_id)

    return render_template(
        "album.html",
        page_title=album.get("name", "Альбом"),
        active_page="albums",
        album=album,
    )
