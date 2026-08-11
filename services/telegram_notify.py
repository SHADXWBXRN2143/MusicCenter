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

 Version : 0.2
===========================================================
"""

import requests

import config
from services import settings_service
from services.artwork import get_cover

API_BASE = "https://api.telegram.org/bot{token}/{method}"


def _format_time(seconds):
    try:
        seconds = int(seconds or 0)
    except (TypeError, ValueError):
        seconds = 0

    minutes, sec = divmod(seconds, 60)
    return f"{minutes}:{sec:02d}"


def _caption(track):
    lines = [f"🎵 <b>{track.get('title') or '—'}</b>"]

    if track.get("artist"):
        lines.append(track["artist"])

    if track.get("album"):
        lines.append(f"<i>{track['album']}</i>")

    if track.get("duration"):
        lines.append(f"⏱ {_format_time(track['duration'])}")

    return "\n".join(lines)


class TelegramNotifyService:

    def __init__(self):
        self.configured = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_ALLOWED_IDS)

    def notify_track(self, track):
        if not self.configured:
            return

        if not settings_service.load().get("telegram_notify_enabled"):
            return

        caption = _caption(track)
        cover = get_cover(track.get("coverArt"))

        for chat_id in config.TELEGRAM_ALLOWED_IDS:
            try:
                if cover:
                    self._send_photo(chat_id, cover, caption)
                else:
                    self._send_message(chat_id, caption)
            except Exception as e:
                print("Telegram notify error:", e)

    def _send_message(self, chat_id, text):
        url = API_BASE.format(token=config.TELEGRAM_BOT_TOKEN, method="sendMessage")
        requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=5,
        )

    def _send_photo(self, chat_id, cover_bytes, caption):
        url = API_BASE.format(token=config.TELEGRAM_BOT_TOKEN, method="sendPhoto")
        requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
            files={"photo": ("cover.jpg", cover_bytes, "image/jpeg")},
            timeout=10,
        )


telegram_notify = TelegramNotifyService()
