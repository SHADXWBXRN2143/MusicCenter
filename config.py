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

# ALSA by default: mpv running under systemd (not an interactive login
# session) can't reach the user's PipeWire/PulseAudio session, so it
# needs to talk to the sound card directly. Override via env if you
# need a specific ALSA device, e.g. "alsa/hw:1,0", or "pulse"/"pipewire"
# when running mpv interactively instead of as a systemd service.
PLAYER_AUDIO_OUTPUT = os.getenv("PLAYER_AUDIO_OUTPUT", "alsa")

# Fade-in/fade-out duration (seconds) applied at the start of every track
# and just before it ends, plus mpv's own --gapless-audio - together they
# read like a crossfade without the fragility of real overlapping playback.
PLAYER_FADE_SECONDS = float(os.getenv("PLAYER_FADE_SECONDS", "2.5"))

# ----------------------------------------------------------
# LIVE SPECTRUM (optional)
# ----------------------------------------------------------

# Off by default - only starts if a capture device is configured (needs an
# ALSA loopback set up on the host, see README). Requires numpy + pyalsaaudio,
# which are NOT in requirements.txt on purpose: this is opt-in hardware setup,
# not something that should be able to break `pip install -r requirements.txt`
# for everyone else.
SPECTRUM_CAPTURE_DEVICE = os.getenv("SPECTRUM_CAPTURE_DEVICE", "")
SPECTRUM_BAR_COUNT = 32
SPECTRUM_GAIN = float(os.getenv("SPECTRUM_GAIN", "4000"))

# ----------------------------------------------------------
# LAST.FM SCROBBLING (optional)
# ----------------------------------------------------------

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY", "")
LASTFM_API_SECRET = os.getenv("LASTFM_API_SECRET", "")
LASTFM_SESSION_KEY = os.getenv("LASTFM_SESSION_KEY", "")

# ----------------------------------------------------------
# LIBRARY
# ----------------------------------------------------------

RECENT_ALBUM_COUNT = 12
RECENT_ARTIST_COUNT = 12
RECENT_TRACK_COUNT = 20

SEARCH_MIN_CHARACTERS = 2
