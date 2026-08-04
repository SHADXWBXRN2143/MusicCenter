"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Telegram Bot Configuration

 Separate process from the web app - talks to it over the
 local REST API instead of importing its code directly, so
 either side can restart independently.

 Version : 0.1
===========================================================
"""

import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

ALLOWED_USER_IDS = {
    int(uid.strip())
    for uid in os.getenv("TELEGRAM_ALLOWED_IDS", "").split(",")
    if uid.strip()
}

API_BASE_URL = os.getenv("MUSICCENTER_API_URL", "http://127.0.0.1:5000")

API_TIMEOUT = 10
