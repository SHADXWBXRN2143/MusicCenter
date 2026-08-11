"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Flask Application Core

 Version : 0.2
===========================================================
"""

from flask import Flask, jsonify, redirect, request, send_from_directory, session

import config
from services import settings_service

from routes.home import home_bp
from routes.albums import albums_bp
from routes.artists import artists_bp
from routes.search import search_bp
from routes.cover import cover_bp
from routes.player import player_bp
from routes.favorites import favorites_bp
from routes.playlists import playlists_bp
from routes.kiosk import kiosk_bp
from routes.settings import settings_bp
from routes.auth import auth_bp


# Endpoints reachable with no PIN even when one is configured - the
# login page itself, static assets, and the service worker (needed to
# even render the login page).
PIN_EXEMPT_ENDPOINTS = {"auth.login", "auth.logout", "static", "service_worker"}

# JSON API routes get a 401 instead of a redirect - they're called by
# page JS (static/js/api.js), never navigated to directly. Every
# player_bp route is JSON-only, so that whole blueprint qualifies by
# prefix; favorites/playlists/search mix HTML pages with JSON routes
# under the same blueprint, so those need to be named individually
# rather than matched by path (e.g. "/playlists/<id>" is an HTML page,
# not JSON, even though it shares a prefix with "/playlists/<id>/add").
JSON_API_ENDPOINTS = {
    "favorites.star", "favorites.unstar",
    "playlists.playlists_api", "playlists.create", "playlists.add_track",
    "playlists.remove_track", "playlists.delete",
    "search.search_api", "search.suggestions",
}


def _is_json_endpoint(endpoint):
    return bool(endpoint) and (
        endpoint.startswith("player.") or endpoint in JSON_API_ENDPOINTS
    )


def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # ==========================================
    # Configuration
    # ==========================================

    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["APP_NAME"] = config.APP_NAME

    # ==========================================
    # Context Variables
    # ==========================================

    @app.context_processor
    def inject_globals():
        return {
            "APP_NAME": config.APP_NAME,
            "pin_enabled": settings_service.has_pin(),
        }

    # ==========================================
    # PIN Access Gate
    #
    # Off entirely until a PIN is set in /settings. Localhost is
    # always exempt - the Telegram bot (bot/api_client.py) calls
    # /player/* etc. unauthenticated from 127.0.0.1 and gates its
    # own users via TELEGRAM_ALLOWED_IDS instead. /kiosk is always
    # exempt too - it's the screen on the Pi itself, not a page
    # meant to be reached from elsewhere on the network.
    # ==========================================

    @app.before_request
    def require_pin():
        if request.endpoint in PIN_EXEMPT_ENDPOINTS:
            return None

        if request.endpoint and request.endpoint.startswith("kiosk."):
            return None

        if request.remote_addr in ("127.0.0.1", "::1"):
            return None

        if not settings_service.has_pin():
            return None

        if session.get("authenticated"):
            return None

        if _is_json_endpoint(request.endpoint):
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        return redirect(f"/login?next={request.path}")

    @app.template_filter("duration")
    def format_duration(seconds):
        try:
            seconds = int(seconds)
        except (TypeError, ValueError):
            return ""

        minutes, sec = divmod(seconds, 60)
        return f"{minutes}:{sec:02d}"

    # ==========================================
    # Blueprints
    # ==========================================

    app.register_blueprint(home_bp)
    app.register_blueprint(artists_bp, url_prefix="/artists")
    app.register_blueprint(albums_bp, url_prefix="/albums")
    app.register_blueprint(search_bp, url_prefix="/search")
    app.register_blueprint(cover_bp)
    app.register_blueprint(player_bp, url_prefix="/player")
    app.register_blueprint(favorites_bp, url_prefix="/favorites")
    app.register_blueprint(playlists_bp, url_prefix="/playlists")
    app.register_blueprint(kiosk_bp, url_prefix="/kiosk")
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)

    # ==========================================
    # Service Worker
    #
    # Served from the root path (not /static/) so its
    # default scope covers the whole site, not just /static/.
    # ==========================================

    @app.route("/sw.js")
    def service_worker():
        return send_from_directory(
            "static/js", "sw.js", mimetype="application/javascript"
        )

    # ==========================================
    # Errors
    # ==========================================

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Page not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=False,
    )
