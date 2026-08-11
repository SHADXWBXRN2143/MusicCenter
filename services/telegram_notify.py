"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Telegram Track Notifications

 Optional now-playing push to Telegram - talks to the Bot API
 directly over HTTP instead of importing bot/ (kept a separate
 process on purpose, see bot/config.py). No-ops quietly when
 not configured or switched off in /settings, same
 degrade-gracefully approach as LastfmService.

 Version : 0.1
===========================================================
"""

import requests

import config
from services import settings_service

API_URL = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifyService:

    def __init__(self):
        self.configured = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_ALLOWED_IDS)

    def notify_track(self, track):
        if not self.configured:
            return

        if not settings_service.load().get("telegram_notify_enabled"):
            return

        title = track.get("title") or "—"
        artist = track.get("artist") or ""

        text = f"🎵 {title}" + (f"\n{artist}" if artist else "")
        url = API_URL.format(token=config.TELEGRAM_BOT_TOKEN)

        for chat_id in config.TELEGRAM_ALLOWED_IDS:
            try:
                requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
            except Exception as e:
                print("Telegram notify error:", e)


telegram_notify = TelegramNotifyService()
