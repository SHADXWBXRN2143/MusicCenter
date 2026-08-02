"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Cover Art Routes

 Version : 0.2
===========================================================
"""

import io

from flask import Blueprint, send_file

from services.artwork import get_cover


cover_bp = Blueprint("cover", __name__)


@cover_bp.route("/cover/<cover_id>")
def cover(cover_id):

    image = get_cover(cover_id)

    if not image:
        return "", 204

    return send_file(io.BytesIO(image), mimetype="image/jpeg")
