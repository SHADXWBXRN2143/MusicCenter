"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Bot Message Formatting

 Version : 0.1
===========================================================
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def format_time(seconds):
    try:
        seconds = int(seconds or 0)
    except (TypeError, ValueError):
        seconds = 0

    minutes, sec = divmod(seconds, 60)
    return f"{minutes}:{sec:02d}"


def now_playing_text(state):
    if not state:
        return "Не удалось получить статус плеера."

    track = state.get("track")

    if not track:
        return "🎵 Ничего не играет"

    lines = [
        f"🎵 <b>{track.get('title', '—')}</b>",
        track.get("artist") or "",
        "",
        (
            f"{'⏸ Пауза' if state.get('paused') else '▶ Играет'} · "
            f"{format_time(state.get('position'))} / {format_time(state.get('duration'))} · "
            f"🔊 {state.get('volume', 0)}"
        ),
    ]

    if state.get("available") is False:
        lines.append("")
        lines.append("⚠️ mpv не найден на устройстве — звука не будет.")

    return "\n".join(lines)


def now_playing_keyboard(state):
    paused = not state or state.get("paused", True)

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏮", callback_data="prev"),
            InlineKeyboardButton("▶" if paused else "⏸", callback_data="toggle"),
            InlineKeyboardButton("⏭", callback_data="next"),
        ],
        [
            InlineKeyboardButton("🔉 -10", callback_data="vol_down"),
            InlineKeyboardButton("🔄", callback_data="refresh"),
            InlineKeyboardButton("🔊 +10", callback_data="vol_up"),
        ],
    ])
