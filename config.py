"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Configuration

 Version : 0.2
===========================================================
"""

from pathlib import Path
import os

# ----------------------------------------------------------
# PATHS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
ARTWORK_CACHE_DIR = CACHE_DIR / "artwork"

for directory in (DATA_DIR, CACHE_DIR, ARTWORK_CACHE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# FLASK
# ----------------------------------------------------------

APP_NAME = "MusicCenter"

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "musiccenter-development-key-change-this"
)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ----------------------------------------------------------
# AIRSONIC / SUBSONIC
# ----------------------------------------------------------

AIRSONIC_URL = os.getenv(
    "AIRSONIC_URL",
    "http://airsonic.local:4040"
)

AIRSONIC_USERNAME = os.getenv("AIRSONIC_USERNAME", "")
AIRSONIC_PASSWORD = os.getenv("AIRSONIC_PASSWORD", "")

AIRSONIC_API_VERSION = "1.15.0"
AIRSONIC_CLIENT_NAME = "MusicCenter"
AIRSONIC_TIMEOUT = int(os.getenv("AIRSONIC_TIMEOUT", "10"))

# ----------------------------------------------------------
# ARTWORK CACHE
# ----------------------------------------------------------

ARTWORK_CACHE_DAYS = 30

# ----------------------------------------------------------
# PLAYER (mpv)
# ----------------------------------------------------------

PLAYER_DEFAULT_VOLUME = int(os.getenv("PLAYER_DEFAULT_VOLUME", "70"))

MPV_SOCKET_PATH = os.getenv(
    "MPV_SOCKET_PATH",
    "/tmp/musiccenter-mpv.sock"
)

# ----------------------------------------------------------
# LIBRARY
# ----------------------------------------------------------

RECENT_ALBUM_COUNT = 12
RECENT_ARTIST_COUNT = 12
RECENT_TRACK_COUNT = 20

SEARCH_MIN_CHARACTERS = 2
