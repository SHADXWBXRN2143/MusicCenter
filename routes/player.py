"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Player Routes

 REST control surface for the local mpv playback on the
 Raspberry Pi. The browser never plays audio itself - it
 only sends commands here and polls /state.

 Version : 0.2
===========================================================
"""

from flask import Blueprint, jsonify, request

from core.player import player
from services.airsonic_service import service
from services.queue import queue


player_bp = Blueprint("player", __name__)


def _state_response():
    return jsonify({"success": True, "state": queue.get_state()})


def _resolve_tracks(payload):
    """
    Builds a normalized track list (with stream urls) from a
    play/queue request payload.
    """

    kind = payload.get("kind")

    if kind == "album":
        album = service.get_album(payload.get("id"))
        return album.get("tracks", [])

    if kind == "track":
        song = service.get_song(payload.get("id"))
        return [song] if song else []

    if kind == "tracks":
        tracks = []

        for song_id in payload.get("ids", []):
            song = service.get_song(song_id)

            if song:
                tracks.append(song)

        return tracks

    return []


# ==========================
# STATE
# ==========================

@player_bp.route("/state")
def state():
    return _state_response()


# ==========================
# PLAYBACK
# ==========================

@player_bp.route("/play", methods=["POST"])
def play():
    payload = request.get_json(silent=True) or {}

    tracks = _resolve_tracks(payload)

    if not tracks:
        return jsonify({"success": False, "message": "Ничего не найдено"}), 404

    index = int(payload.get("index", 0))
    queue.set_queue(tracks, start_index=index)

    return _state_response()


@player_bp.route("/toggle", methods=["POST"])
def toggle():
    player.toggle()
    return _state_response()


@player_bp.route("/next", methods=["POST"])
def next_track():
    queue.next(user_initiated=True)
    return _state_response()


@player_bp.route("/previous", methods=["POST"])
def previous_track():
    queue.previous()
    return _state_response()


@player_bp.route("/seek", methods=["POST"])
def seek():
    payload = request.get_json(silent=True) or {}
    player.seek(float(payload.get("position", 0)))
    return _state_response()


@player_bp.route("/volume", methods=["POST"])
def volume():
    payload = request.get_json(silent=True) or {}
    player.set_volume(payload.get("value", 70))
    return _state_response()


@player_bp.route("/shuffle", methods=["POST"])
def shuffle():
    queue.toggle_shuffle()
    return _state_response()


@player_bp.route("/repeat", methods=["POST"])
def repeat():
    queue.cycle_repeat()
    return _state_response()


# ==========================
# QUEUE
# ==========================

@player_bp.route("/queue/add", methods=["POST"])
def queue_add():
    payload = request.get_json(silent=True) or {}

    for track in _resolve_tracks(payload):
        queue.add(track)

    return _state_response()


@player_bp.route("/queue/clear", methods=["POST"])
def queue_clear():
    queue.clear()
    return _state_response()
