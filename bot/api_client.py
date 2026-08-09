"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Bot API Client

 Thin wrapper around the same /player/* and /search/api
 REST endpoints the web UI uses (see static/js/api.js).

 Version : 0.1
===========================================================
"""

import requests

from bot.config import API_BASE_URL, API_TIMEOUT


def _get(path, params=None):
    try:
        response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=API_TIMEOUT)
        return response.json()
    except Exception as e:
        print(f"Bot API GET error {path}: {e}")
        return None


def _post(path, payload=None):
    try:
        response = requests.post(f"{API_BASE_URL}{path}", json=payload or {}, timeout=API_TIMEOUT)
        return response.json()
    except Exception as e:
        print(f"Bot API POST error {path}: {e}")
        return None


def get_state():
    # /player/state responds {"success": .., "state": {...}} - every
    # caller here wants the flat state dict, not the wrapper.
    data = _get("/player/state")

    if not data or not data.get("success"):
        return None

    return data.get("state")


def play(payload):
    return _post("/player/play", payload)


def toggle():
    return _post("/player/toggle")


def next_track():
    return _post("/player/next")


def previous_track():
    return _post("/player/previous")


def set_volume(value):
    return _post("/player/volume", {"value": value})


def cycle_repeat():
    return _post("/player/repeat")


def search(query):
    return _get("/search/api", {"q": query})
