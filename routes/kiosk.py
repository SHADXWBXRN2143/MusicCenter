"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Kiosk Routes

 A standalone "now playing" page meant for a small screen
 attached directly to the Pi (Chromium in --kiosk mode) -
 no sidebar/navigation, just the player.

 Version : 0.1
===========================================================
"""

from flask import Blueprint, render_template

kiosk_bp = Blueprint("kiosk", __name__)


@kiosk_bp.route("/")
def kiosk():
    return render_template("kiosk.html")
