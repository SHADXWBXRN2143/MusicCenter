"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Settings Routes

 Version : 0.1
===========================================================
"""

from flask import Blueprint, redirect, render_template, request

from core.player import EQ_PRESETS, player
from services import settings_service


settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings")
def settings_page():
    return render_template(
        "settings.html",
        page_title="Настройки",
        active_page="settings",
        settings=settings_service.load(),
        eq_presets=list(EQ_PRESETS.keys()),
    )


@settings_bp.route("/settings/save", methods=["POST"])
def save_settings():
    form = request.form

    try:
        volume = max(0, min(100, int(form.get("default_volume", 70))))
    except ValueError:
        volume = 70

    eq_preset = form.get("eq_preset", "flat")

    if eq_preset not in EQ_PRESETS:
        eq_preset = "flat"

    audio_output = form.get("audio_output", "").strip() or "alsa"
    telegram_notify_enabled = form.get("telegram_notify_enabled") == "on"

    settings_service.save({
        "default_volume": volume,
        "eq_preset": eq_preset,
        "audio_output": audio_output,
        "telegram_notify_enabled": telegram_notify_enabled,
    })

    # Volume/EQ take effect immediately on the already-running mpv;
    # audio_output only applies on the next mpv (re)start.
    player.set_volume(volume)
    player.set_eq(eq_preset)

    return redirect("/settings?saved=1")


@settings_bp.route("/settings/pin", methods=["POST"])
def save_pin():
    new_pin = request.form.get("new_pin", "").strip()
    confirm_pin = request.form.get("confirm_pin", "").strip()

    if new_pin and new_pin != confirm_pin:
        return redirect("/settings?pin_mismatch=1")

    settings_service.set_pin(new_pin)

    return redirect("/settings?pin_saved=1")
