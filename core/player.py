"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 MPV Player

 Controls a local mpv process (audio only) over its JSON IPC
 socket. This is what actually makes sound come out of the
 Raspberry Pi's audio output into the music center - the web
 UI is only a remote control.

 If the `mpv` binary isn't installed, the player marks itself
 unavailable and every method degrades gracefully instead of
 raising, so the rest of the site keeps working.

 Version : 0.2
===========================================================
"""

import atexit
import json
import os
import shutil
import socket
import subprocess
import threading
import time

import config


# Filter chains for the `af` mpv property (ffmpeg's `equalizer`, applied via
# lavfi). "flat" means no equalizer stage at all - not an empty filter, which
# mpv would reject.
EQ_PRESETS = {
    "flat": None,
    "bass": "equalizer=f=80:width_type=o:width=1:g=8,equalizer=f=200:width_type=o:width=1:g=3",
    "vocal": "equalizer=f=1000:width_type=o:width=1.2:g=5,equalizer=f=3000:width_type=o:width=1.2:g=3",
    "treble": "equalizer=f=6000:width_type=o:width=1:g=6,equalizer=f=10000:width_type=o:width=1:g=4",
    "vshape": "equalizer=f=80:width_type=o:width=1:g=6,equalizer=f=1000:width_type=o:width=1:g=-3,equalizer=f=8000:width_type=o:width=1:g=6",
}


class MPVPlayer:

    def __init__(self):
        self.socket_path = config.MPV_SOCKET_PATH
        self.available = False

        self.on_track_end = None

        self._process = None
        self._lock = threading.Lock()

        self._expect_track = False
        self._track_started = False

        self._sleep_timer = None
        self._sleep_deadline = None

        self._eq_preset = "flat"
        self._fade_out_triggered = False

        self._start()

    # ==========================
    # LIFECYCLE
    # ==========================

    def _start(self):
        mpv_bin = shutil.which("mpv")

        if not mpv_bin:
            print("MPVPlayer: 'mpv' binary not found - playback disabled")
            return

        try:
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
        except OSError:
            pass

        try:
            self._process = subprocess.Popen(
                [
                    mpv_bin,
                    "--idle=yes",
                    "--no-video",
                    "--no-terminal",
                    "--gapless-audio=yes",
                    f"--ao={config.PLAYER_AUDIO_OUTPUT}",
                    f"--input-ipc-server={self.socket_path}",
                    f"--volume={config.PLAYER_DEFAULT_VOLUME}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print("MPVPlayer: failed to start mpv:", e)
            return

        for _ in range(50):
            if os.path.exists(self.socket_path):
                self.available = True
                break
            time.sleep(0.1)

        if not self.available:
            print("MPVPlayer: mpv did not create its IPC socket in time")
            return

        atexit.register(self._shutdown)

        threading.Thread(target=self._watch_loop, daemon=True).start()

    def _shutdown(self):
        if self._process:
            self._process.terminate()

    # ==========================
    # IPC
    # ==========================

    def _send(self, command):
        if not self.available:
            return None

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect(self.socket_path)
                sock.sendall((json.dumps({"command": command}) + "\n").encode())

                data = b""
                while b"\n" not in data:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk

                if not data:
                    return None

                return json.loads(data.split(b"\n")[0].decode())
        except Exception as e:
            print("MPVPlayer IPC error:", e)
            return None

    def _get_property(self, name, default=None):
        response = self._send(["get_property", name])

        if response and response.get("error") == "success":
            value = response.get("data")
            return value if value is not None else default

        return default

    def _set_property(self, name, value):
        self._send(["set_property", name, value])

    # ==========================
    # TRANSPORT
    # ==========================

    def load(self, url):
        with self._lock:
            self._send(["loadfile", url, "replace"])
            self._set_property("pause", False)
            self._track_started = False
            self._expect_track = True
            self._fade_out_triggered = False
            self._apply_af(f"afade=t=in:st=0:d={config.PLAYER_FADE_SECONDS}")

    def play(self):
        self._set_property("pause", False)

    def pause(self):
        self._set_property("pause", True)

    def toggle(self):
        paused = bool(self._get_property("pause", True))
        self._set_property("pause", not paused)

    def stop(self):
        with self._lock:
            self._send(["stop"])
            self._expect_track = False
            self._track_started = False

    def seek(self, seconds):
        self._send(["seek", seconds, "absolute"])

    def set_volume(self, value):
        value = max(0, min(100, int(value)))
        self._set_property("volume", value)

    # ==========================
    # EQ / FADE TRANSITIONS
    # ==========================

    def _apply_af(self, fade_filter=None):
        """
        Rebuilds the `af` property from the current EQ preset plus an
        optional fade-in/fade-out filter. Both live in one lavfi graph
        since mpv's `af` is a single player-wide property, not per-file.
        """

        parts = []

        eq = EQ_PRESETS.get(self._eq_preset)
        if eq:
            parts.append(eq)

        if fade_filter:
            parts.append(fade_filter)

        af = f"lavfi=[{','.join(parts)}]" if parts else ""
        self._set_property("af", af)

    def set_eq(self, preset):
        if preset not in EQ_PRESETS:
            return

        self._eq_preset = preset
        self._apply_af()

    # ==========================
    # SLEEP TIMER
    # ==========================

    def set_sleep(self, minutes):
        self.cancel_sleep()

        minutes = max(1, float(minutes))
        self._sleep_deadline = time.time() + minutes * 60

        self._sleep_timer = threading.Timer(minutes * 60, self._sleep_fire)
        self._sleep_timer.daemon = True
        self._sleep_timer.start()

    def cancel_sleep(self):
        if self._sleep_timer:
            self._sleep_timer.cancel()

        self._sleep_timer = None
        self._sleep_deadline = None

    def _sleep_fire(self):
        self._sleep_timer = None
        self._sleep_deadline = None
        self.pause()

    def _sleep_remaining(self):
        if not self._sleep_deadline:
            return None

        return max(0, round(self._sleep_deadline - time.time()))

    # ==========================
    # STATE
    # ==========================

    def get_state(self):
        if not self.available:
            return {
                "available": False,
                "paused": True,
                "position": 0,
                "duration": 0,
                "volume": config.PLAYER_DEFAULT_VOLUME,
                "sleep_remaining": self._sleep_remaining(),
                "eq_preset": self._eq_preset,
            }

        return {
            "available": True,
            "paused": bool(self._get_property("pause", True)),
            "position": self._get_property("time-pos", 0) or 0,
            "duration": self._get_property("duration", 0) or 0,
            "volume": self._get_property("volume", config.PLAYER_DEFAULT_VOLUME),
            "sleep_remaining": self._sleep_remaining(),
            "eq_preset": self._eq_preset,
        }

    # ==========================
    # END-OF-TRACK WATCHER
    # ==========================

    def _watch_loop(self):
        while True:
            time.sleep(0.5)

            if not self.available or not self._expect_track:
                continue

            idle = bool(self._get_property("idle-active", False))

            if not self._track_started:
                if not idle:
                    self._track_started = True
                continue

            if idle:
                self._expect_track = False
                self._track_started = False

                if self.on_track_end:
                    try:
                        self.on_track_end()
                    except Exception as e:
                        print("MPVPlayer on_track_end error:", e)

                continue

            if not self._fade_out_triggered:
                duration = self._get_property("duration", 0) or 0
                position = self._get_property("time-pos", 0) or 0
                remaining = duration - position

                if duration and 0 < remaining <= config.PLAYER_FADE_SECONDS:
                    self._fade_out_triggered = True
                    self._apply_af(f"afade=t=out:st={position}:d={config.PLAYER_FADE_SECONDS}")


player = MPVPlayer()
