"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Favorites Routes

 Version : 0.1
===========================================================
"""

from flask import Blueprint, jsonify, render_template, request

from services.airsonic_service import service


favorites_bp = Blueprint("favorites", __name__)


@favorites_bp.route("/")
def favorites_page():
    results = service.get_favorites()

    return render_template(
        "favorites.html",
        page_title="Избранное",
        active_page="favorites",
        results=results,
    )


@favorites_bp.route("/star", methods=["POST"])
def star():
    payload = request.get_json(silent=True) or {}
    ok = service.star(payload.get("id"), kind=payload.get("kind", "song"))
    return jsonify({"success": ok})


@favorites_bp.route("/unstar", methods=["POST"])
def unstar():
    payload = request.get_json(silent=True) or {}
    ok = service.unstar(payload.get("id"), kind=payload.get("kind", "song"))
    return jsonify({"success": ok})
