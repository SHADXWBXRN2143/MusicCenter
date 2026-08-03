"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Playlist Routes

 Version : 0.1
===========================================================
"""

from flask import Blueprint, jsonify, render_template, request

from services.airsonic_service import service


playlists_bp = Blueprint("playlists", __name__)


@playlists_bp.route("/")
def playlists_page():
    playlists = service.get_playlists()

    return render_template(
        "playlists.html",
        page_title="Плейлисты",
        active_page="playlists",
        playlists=playlists,
    )


@playlists_bp.route("/api")
def playlists_api():
    return jsonify({"success": True, "playlists": service.get_playlists()})


@playlists_bp.route("/<playlist_id>")
def playlist_detail(playlist_id):
    playlist = service.get_playlist(playlist_id)

    return render_template(
        "playlist.html",
        page_title=playlist.get("name", "Плейлист"),
        active_page="playlists",
        playlist=playlist,
    )


@playlists_bp.route("/create", methods=["POST"])
def create():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()

    if not name:
        return jsonify({"success": False, "message": "Введите название"}), 400

    song_id = payload.get("song_id")
    playlist = service.create_playlist(name, song_ids=[song_id] if song_id else None)

    return jsonify({"success": bool(playlist), "playlist": playlist})


@playlists_bp.route("/<playlist_id>/add", methods=["POST"])
def add_track(playlist_id):
    payload = request.get_json(silent=True) or {}
    ok = service.add_to_playlist(playlist_id, payload.get("song_id"))
    return jsonify({"success": ok})


@playlists_bp.route("/<playlist_id>/remove", methods=["POST"])
def remove_track(playlist_id):
    payload = request.get_json(silent=True) or {}
    ok = service.remove_from_playlist(playlist_id, payload.get("index"))
    return jsonify({"success": ok})


@playlists_bp.route("/<playlist_id>/delete", methods=["POST"])
def delete(playlist_id):
    ok = service.delete_playlist(playlist_id)
    return jsonify({"success": ok})
