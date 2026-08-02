"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Artwork Service

 Disk-cached cover art proxy for the Airsonic server.

 Version : 0.2
===========================================================
"""

import time

import config
from api.airsonic import client


def get_cover(cover_id):
    """
    Returns cover art bytes for a given Airsonic coverArt id,
    using a local disk cache. Returns None if unavailable.
    """

    if not cover_id:
        return None

    cache_file = config.ARTWORK_CACHE_DIR / f"{cover_id}.jpg"

    max_age = config.ARTWORK_CACHE_DAYS * 86400

    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime

        if age < max_age:
            return cache_file.read_bytes()

    try:
        image = client.get_cover_art(cover_id)

        if not image:
            return None

        cache_file.write_bytes(image)

        return image
    except Exception as e:
        print(f"Artwork error ({cover_id}):", e)

        if cache_file.exists():
            return cache_file.read_bytes()

        return None
