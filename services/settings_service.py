"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Settings Service

 Runtime-editable settings (as opposed to config.py's env-var
 deploy config) - default volume/EQ/audio output, web access
 PIN, Telegram notification toggle. Persisted to data/settings.json
 so changes made from the /settings page survive restarts
 without hand-editing .env.

 Version : 0.1
===========================================================
"""

import hashlib
import json
import threading

import config

SETTINGS_PATH = config.DATA_DIR / "settings.json"

DEFAULTS = {
    "default_volume": config.PLAYER_DEFAULT_VOLUME,
    "eq_preset": "flat",
    "audio_output": config.PLAYER_AUDIO_OUTPUT,
    "pin_hash": "",
    "telegram_notify_enabled": False,
}

_lock = threading.Lock()


def _hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def load():
    with _lock:
        if not SETTINGS_PATH.exists():
            return dict(DEFAULTS)

        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return dict(DEFAULTS)

        merged = dict(DEFAULTS)
        merged.update(data)
        return merged


def save(values):
    with _lock:
        current = dict(DEFAULTS)

        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    current.update(json.load(f))
            except (OSError, ValueError):
                pass

        current.update(values)

        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)

        return current


def set_pin(pin):
    return save({"pin_hash": _hash_pin(pin) if pin else ""})


def check_pin(pin):
    settings = load()

    if not settings.get("pin_hash"):
        return True

    return _hash_pin(pin or "") == settings["pin_hash"]


def has_pin():
    return bool(load().get("pin_hash"))
