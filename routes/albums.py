"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Album Routes

 Version : 0.2
===========================================================
"""

from flask import Blueprint, render_template

from services.airsonic_service import service


albums_bp = Blueprint("albums", __name__)


@albums_bp.route("/")
def albums():

    albums = service.get_albums(limit=200)

    return render_template(
        "albums.html",
        page_title="Альбомы",
        active_page="albums",
        albums=albums,
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
