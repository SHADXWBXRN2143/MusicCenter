"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Flask Application Core

 Version : 0.2
===========================================================
"""

from flask import Flask, jsonify

import config

from routes.home import home_bp
from routes.albums import albums_bp
from routes.artists import artists_bp
from routes.search import search_bp
from routes.cover import cover_bp
from routes.player import player_bp


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
        return {"APP_NAME": config.APP_NAME}

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
