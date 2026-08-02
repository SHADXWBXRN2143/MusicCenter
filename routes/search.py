"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Search Routes

 Version : 0.2
===========================================================
"""

from flask import Blueprint, jsonify, render_template, request

from services.airsonic_service import service


search_bp = Blueprint("search", __name__)

EMPTY_RESULTS = {"artists": [], "albums": [], "songs": []}


# =========================================================
# Search Page
# =========================================================

@search_bp.route("/")
def search_page():

    query = request.args.get("q", "")
    results = service.search(query) if query else EMPTY_RESULTS

    return render_template(
        "search.html",
        page_title="Поиск",
        active_page="search",
        query=query,
        results=results,
    )


# =========================================================
# AJAX Search
# =========================================================

@search_bp.route("/api")
def search_api():

    query = request.args.get("q", "")

    if not query:
        return jsonify({"success": False, "message": "Пустой запрос"})

    return jsonify({"success": True, "results": service.search(query)})


# =========================================================
# Suggestions
# =========================================================

@search_bp.route("/suggestions")
def suggestions():

    query = request.args.get("q", "")

    if len(query) < 2:
        return jsonify({"success": True, "items": []})

    results = service.search(query)
    items = []

    for artist in results["artists"]:
        items.append({
            "type": "artist",
            "id": artist["id"],
            "title": artist["name"],
        })

    for album in results["albums"]:
        items.append({
            "type": "album",
            "id": album["id"],
            "title": album["name"],
            "artist": album.get("artist"),
        })

    for song in results["songs"]:
        items.append({
            "type": "track",
            "id": song["id"],
            "title": song["title"],
            "artist": song.get("artist"),
        })

    return jsonify({"success": True, "items": items[:10]})
